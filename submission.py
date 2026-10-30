"""
CSC4001 Software Testing Assignment - MiniRedis Test Suite
submission.py - Contains fuzzer and metamorphic_relations functions
"""

import random


def fuzzer(seed: int, num_cases: int) -> list[str]:
    """
    Generate random test cases for MiniRedis.
    
    Args:
        seed: Random seed for reproducibility
        num_cases: Number of test cases to generate
    
    Returns:
        List of MiniRedis commands
    """
    random.seed(seed)
    commands = []
    
    # Command template definitions - balanced coverage
    string_commands = [
        "SET", "GET", "DEL", "EXISTS", "INCR", "DECR",
        "INCRBY", "DECRBY", "APPEND", "STRLEN", "GETRANGE",
        "MSET", "MGET"
    ]
    
    list_commands = [
        "LPUSH", "RPUSH", "LPOP", "RPOP", "LLEN",
        "LRANGE", "LINDEX", "LSET", "LREM", "LREV"
    ]
    
    expression_commands = [
        "EVAL", "CALC"
    ]
    
    validation_commands = [
        "DEFINE", "SETV", "VALIDATE"
    ]
    
    # Helper functions
    def random_key():
        return f"k{random.randint(0, 100)}"
    
    def random_value():
        return f"v{random.randint(0, 200)}"
    
    def random_number():
        return random.randint(-500, 500)
    
    def random_expr(depth=3):
        """Generate random S-expressions"""
        if depth <= 0 or random.random() < 0.25:
            if random.random() < 0.5:
                return str(random_number())
            else:
                return f"$x{random.randint(0, 8)}"
        
        op = random.choice(['+', '-', '*', '/', '%', '<', '>', '<=', '>=', '==', '!=', 'and', 'or', 'not'])
        
        if op == 'not':
            return f"(not {random_expr(depth - 1)})"
        elif op == 'if':
            cond = random_expr(max(0, depth - 1))
            true_val = random_expr(max(0, depth - 1))
            false_val = random_expr(max(0, depth - 1))
            return f"(if {cond} {true_val} {false_val})"
        elif op in ['and', 'or']:
            arg1 = random_expr(max(0, depth - 1))
            arg2 = random_expr(max(0, depth - 1))
            return f"({op} {arg1} {arg2})"
        else:
            arg1 = random_expr(depth - 1)
            arg2 = random_expr(depth - 1)
            return f"({op} {arg1} {arg2})"
    
    def generate_string_command():
        cmd = random.choice(string_commands)
        k = random_key()
        
        if cmd == "SET":
            # Various value types to trigger different branches
            value_choices = [
                random_value(),  # regular value
                str(random_number()),  # numeric value
                "",  # empty string
                "test", "hello",  # English text
                
                "a" * 20,  # long string
                "0", "-1", "999",  # special numbers
            ]
            v = random.choice(value_choices)
            return f"SET {k} {v}"
        elif cmd == "GET":
            return f"GET {k}"
        elif cmd == "DEL":
            # DEL command key branches: delete one vs multiple, exists vs not
            num_keys = random.randint(1, 6)
            keys = " ".join([random_key() for _ in range(num_keys)])
            return f"DEL {keys}"
        elif cmd == "EXISTS":
            num_keys = random.randint(1, 6)
            keys = " ".join([random_key() for _ in range(num_keys)])
            return f"EXISTS {keys}"
        elif cmd == "INCR":
            return f"INCR {k}"
        elif cmd == "DECR":
            return f"DECR {k}"
        elif cmd == "INCRBY":
            delta = random.choice([1, 2, 5, 10, 50, 100, -1, -5, -10])
            return f"INCRBY {k} {delta}"
        elif cmd == "DECRBY":
            delta = random.choice([1, 2, 5, 10, 50, 100, -1, -5, -10])
            return f"DECRBY {k} {delta}"
        elif cmd == "APPEND":
            # APPEND branches: append to existing vs new key
            suffix = random.choice([random_value(), '', 'x', 'suffix', 'long_suffix_here'])
            return f"APPEND {k} {suffix}"
        elif cmd == "STRLEN":
            return f"STRLEN {k}"
        elif cmd == "GETRANGE":
            # GETRANGE key: various index combinations
            scenarios = [
                (0, 0),  # single character
                (0, -1),  # all
                (-1, -1),  # last character
                (0, 5),  # first few
                (-5, -1),  # last few
                (10, 20),  # out of range
                (-20, -10),  # negative index out of range
                (0, 100),  # range too large
                (1, 3),  # start < end normal case
                (2, 4),  # start < end normal case
                (0, 1),  # first 2
            ]
            start, end = random.choice(scenarios)
            return f"GETRANGE {k} {start} {end}"
        elif cmd == "MSET":
            # MSET key branches: even vs odd parameter count (trigger error)
            num_pairs = random.randint(2, 5)
            pairs = []
            for _ in range(num_pairs):
                pairs.extend([random_key(), random_value()])
            return f"MSET {' '.join(pairs)}"
        elif cmd == "MGET":
            # MGET key branches: all exist vs partially missing vs all missing
            num_keys = random.randint(1, 6)
            keys = " ".join([random_key() for _ in range(num_keys)])
            return f"MGET {keys}"
        return f"SET {k} {random_value()}"
    
    def generate_list_command():
        cmd = random.choice(list_commands)
        k = random_key()
        
        if cmd == "LPUSH":
            # LPUSH key branches: single vs multiple elements, empty element
            vals = " ".join([random.choice([random_value(), str(random_number()), "item", ""]) for _ in range(random.randint(1, 6))])
            return f"LPUSH {k} {vals}"
        elif cmd == "RPUSH":
            vals = " ".join([random.choice([random_value(), str(random_number()), "item", ""]) for _ in range(random.randint(1, 6))])
            return f"RPUSH {k} {vals}"
        elif cmd == "LPOP":
            return f"LPOP {k}"
        elif cmd == "RPOP":
            return f"RPOP {k}"
        elif cmd == "LLEN":
            return f"LLEN {k}"
        elif cmd == "LRANGE":
            # LRANGE key branches:
            # start < stop vs start > stop (negative case)
            # start out vs stop out vs both out
            # start=0, stop=-1 (all)
            scenarios = [
                (0, -1),  # all
                (0, 2),  # first few
                (-3, -1),  # last few
                (0, 0),  # single
                (5, 10),  # start out
                (0, 100),  # stop out
                (10, 5),  # start > stop
                (-100, -50),  # negative index out
            ]
            start, stop = random.choice(scenarios)
            return f"LRANGE {k} {start} {stop}"
        elif cmd == "LINDEX":
            # LINDEX key branches: 0, positive, negative, out of range
            indices = [0, 1, 2, 5, -1, -2, -5, 100, -100]
            return f"LINDEX {k} {random.choice(indices)}"
        elif cmd == "LSET":
            # LSET key branches: valid vs invalid index
            index = random.choice([0, 1, 2, 5, -1, -2, 100, -100])
            return f"LSET {k} {index} {random_value()}"
        elif cmd == "LREM":
            # LREM key branches: count > 0, count < 0, count = 0
            # and delete existing vs non-existing value
            count = random.choice([-5, -3, -1, 0, 1, 3, 5, 100])
            return f"LREM {k} {count} {random_value()}"
        elif cmd == "LREV":
            return f"LREV {k}"
        return f"LPUSH {k} {random_value()}"
    
    def generate_expression_command():
        cmd = random.choice(expression_commands)
        
        if cmd == "EVAL":
            # Key: cover all operators and branches
            expr_templates = [
                # Arithmetic operations
                f"(+ {random_number()} {random_number()})",
                f"(- {random_number()} {random_number()})",
                f"(* {random_number()} {random_number()})",
                f"(/ {random_number()} {random_number()})",
                f"(% {random_number()} {random_number()})",
                # Division by zero cases - key boundary
                "(/ 1 0)",
                "(% 1 0)",
                "(/ 0 0)",
                "(/ 10 2)",  # exact division
                "(% 10 3)",  # division remainder
                # Comparison operations
                "(< 5 10)",
                "(> 10 5)",
                "(<= 5 5)",
                "(>= 5 5)",
                "(== 5 5)",
                "(!= 5 3)",
                "(< 0 0)",
                "(> 0 0)",
                # Logical operations
                "(and 1 1)",
                "(and 0 1)",
                "(and 0 0)",
                "(and 1 0)",
                "(or 0 0)",
                "(or 0 1)",
                "(or 1 1)",
                "(or 1 0)",
                "(not 0)",
                "(not 1)",
                "(not 2)",
                # Mixed logical
                "(and (or 0 1) (not 0))",
                "(or (and 1 1) (not 0))",
                "(not (and 1 0))",
                "(not (or 0 0))",
                "(and (not 0) (not 1))",
                # if expressions
                "(if 1 100 200)",
                "(if 0 100 200)",
                "(if (< 5 10) 1 0)",
                "(if (> 5 10) 1 0)",
                "(if (== 1 1) 1 0)",
                "(if (!= 1 1) 1 0)",
                # Nested if
                "(if (if 1 0 1) 100 200)",
                "(if (if 0 1 0) 100 200)",
                "(if (if (< 5 10) 1 0) a b)",
                # Variable references
                f"(+ $x{random.randint(0, 8)} $x{random.randint(0, 8)})",
                "(+ $x0 $x0)",
                "(+ $x0 $x1 $x2)",
                "(* $x0 $x0)",
                # Boundary values
                "(+ 0 0)",
                "(- 0 0)",
                "(* 0 100)",
                "(/ 100 100)",
                "(% 100 100)",
                "(/ 0 100)",
                "(% 0 100)",
                # Negative number operations
                "(- 0 5)",
                "(+ -5 5)",
                "(* -2 -3)",
                "(- -10 -5)",
                "(/ -10 2)",
                "(% -10 3)",
                "(+ -1 -1)",
                "(* -1 100)",
                # Nested expressions
                "(+ (* 2 3) (- 10 5))",
                "(* (+ 1 2) (+ 3 4))",
                "(if (> (+ 1 2) 3) (+ 1 2) 0)",
                "(+ (* 2 3) (* 4 5))",
                "(* (+ 1 2) (- 10 5))",
                "(/ (* 10 3) 2)",
                # Multi-argument (possible error branches)
                "(+ 1 2 3 4 5)",
                "(* 1 2 3)",
                "(- 10 5 3)",
                # Random complex expressions
                random_expr(2),
                random_expr(3),
            ]
            return f"EVAL {random.choice(expr_templates)}"
        elif cmd == "CALC":
            k = random_key()
            exprs = [
                f"(+ {random_number()} {random_number()})",
                f"(* {random_number()} {random_number()})",
                "(+ $x0 $x0)",
                random_expr(2),
            ]
            return f"CALC {k} {random.choice(exprs)}"
        return f"EVAL {random_number()}"
    
    def generate_validation_command():
        cmd = random.choice(validation_commands)
        k = random_key()
        
        if cmd == "DEFINE":
            type_choice = random.choice(["integer", "string", "enum"])
            if type_choice == "integer":
                # Key branches: positive range, negative range, include 0, single point, negative range
                min_val = random.randint(-200, 100)
                max_val = min_val + random.randint(10, 300)
                return f"DEFINE {k} TYPE integer RANGE {min_val} {max_val}"
            elif type_choice == "string":
                # Multiple regex patterns to trigger different branches
                patterns = [
                    r'^[a-z]+$',        # lowercase letters
                    r'^[0-9]+$',        # digits
                    r'^[A-Z]+$',        # uppercase letters
                    r'^[a-zA-Z]+$',     # letters
                    r'^[a-z0-9]+$',     # alphanumeric
                    r'^test.*$',         # starts with test
                    r'.*test$',          # ends with test
                    r'^.{3,10}$',       # length limit
                    r'^[a-zA-Z0-9]+$',  # mixed alphanumeric
                    r'^x$',             # single char
                ]
                return f'DEFINE {k} TYPE string PATTERN "{random.choice(patterns)}"'
            else:
                # Enum types - more combinations
                enums = [
                    "active,inactive,pending",
                    "on,off,unknown",
                    "yes,no,maybe",
                    "red,green,blue,yellow",
                    "a,b,c,d,e",
                    "true,false",
                    "admin,user,guest",
                ]
                return f"DEFINE {k} TYPE enum VALUES {random.choice(enums)}"
        elif cmd == "SETV":
            type_choice = random.choice(["integer", "string", "enum"])
            if type_choice == "integer":
                # SETV key: valid vs invalid values (inside/outside boundary)
                val = random.choice([-500, -201, -200, -100, -1, 0, 1, 50, 100, 199, 200, 500])
                return f"SETV {k} {val} TYPE integer RANGE -200 200"
            elif type_choice == "string":
                # Valid vs invalid strings - multiple cases
                strs = random.choice([
                    ("test", True),
                    ("hello", True),
                    ("abc123", True),
                    ("TEST", False),
                    ("123", False),
                    ("test123", True),
                    ("abc", True),
                    ("TEST123", False),
                ])
                val, matches = strs
                if matches:
                    return f'SETV {k} {val} TYPE string PATTERN "^[a-z0-9]+$"'
                else:
                    return f'SETV {k} {val} TYPE string PATTERN "^[a-z]+$"'
            else:
                enums = ["active,inactive", "yes,no", "a,b,c", "true,false"]
                enum = random.choice(enums)
                values = enum.split(',')
                val = random.choice([values[0], "invalid_value", values[-1], "UNKNOWN"])
                return f"SETV {k} {val} TYPE enum VALUES {enum}"
        elif cmd == "VALIDATE":
            return f"VALIDATE {k}"
        return f"DEFINE {k} TYPE integer RANGE 0 100"
    
    def generate_edge_case():
        """Generate edge case tests"""
        cases = [
            # Basic boundaries
            "SET x 0",
            "GET nonexistent_key",
            "DEL nonexistent_key",
            "INCR new_counter",
            "DECR new_counter",
            "APPEND new_key value",
            "GETRANGE x -5 5",
            "GETRANGE gr_key 100 200",
            "LRANGE empty_list 0 -1",
            "LPOP empty_list",
            "LINDEX x 0",
            
            # Expression boundaries
            "EVAL (+ 0 0)",
            "EVAL (- 0 0)",
            "EVAL (* 0 100)",
            "EVAL (/ 100 100)",
            "EVAL (% 100 100)",
            "EVAL (if 0 100 200)",
            "EVAL (if 1 100 200)",
            "EVAL (not 0)",
            "EVAL (not 1)",
            "EVAL (and 0 0)",
            "EVAL (and 1 1)",
            "EVAL (or 0 0)",
            "EVAL (or 1 1)",
            "EVAL (< 1 1)",
            "EVAL (> 1 1)",
            "EVAL (<= 1 1)",
            "EVAL (>= 1 1)",
            "EVAL (== 0 0)",
            "EVAL (!= 0 1)",
            
            # Validation command boundaries
            "SETV edge_key 0 TYPE integer RANGE -10 10",
            "DEFINE test TYPE integer RANGE 0 0",
            "DEFINE test TYPE integer RANGE 0 1",
            'DEFINE test TYPE string PATTERN "^[0-9]+$"',
            
            # Error command formats
            "EXISTS",
            "DEL",
            "SET badnum abc",
            "INCR badnum",
            "DECR badnum",
            "INCRBY badnum 3",
            "DECRBY badnum 3",
            
            # Boolean value tests
            "SET z_true 1",
            "EVAL (and $z_true $z_true)",
            "SET z_false 0",
            "EVAL (or $z_false $z_true)",
            "SET z_one 1",
            "EVAL (== $z_one 1)",
            
            # Comparison operations
            "EVAL (>= 5 5)",
            "EVAL (!= 3 3)",
            "EVAL (<= 2 2)",
            
            # Variable references
            "SET deep_a 1",
            "SET deep_b 2",
            "EVAL (+ $deep_a $deep_b)",
            "SET deep_c 10",
            "EVAL (* $deep_c $deep_c)",
            
            # List boundaries
            "LREM lrem_edge 0 x",
            "LREM lrem_edge2 -1 y",
            "LSET lset_edge 0 v",
            "LREV no_such_list_rev",
            
            # MSET/MGET boundaries
            "MGET only_one k1",
            "MGET k1 k2 k3 k4 k5",
            "MSET pair_a 1 pair_b 2",
            "MSET k1 v1 k2 v2 k3 v3",
            
            # Validation related
            "DEFINE sch_int TYPE integer RANGE 10 20",
            "SET sch_int 5",
            "SET sch_int 25",
            'DEFINE sch_str TYPE string PATTERN "^[0-9]+$"',
            "SET sch_str hello",
            "DEFINE sch_en TYPE enum VALUES a,b",
            "SET sch_en c",
            "VALIDATE sch_int",
            
            # More boundaries
            "SETV inline_bad 999 TYPE integer RANGE 0 10",
            "APPEND append_new_only tail",
            "GET append_new_only",
            
            # Operation chains
            "SET dec_chain 10", "DECRBY dec_chain 3", "INCRBY dec_chain 3", "GET dec_chain",
            "SET rng_flip abc", "GETRANGE rng_flip 2 1",
            "LPUSH lpush_rpush_mix 1", "RPUSH lpush_rpush_mix 2", "LRANGE lpush_rpush_mix 0 -1",
            
            # Division by zero tests
            "EVAL (/ 1 0)",
            "EVAL (% 1 0)",
            "EVAL (/ 0 0)",
            
            # Duplicate definitions
            "DEFINE cov_dup TYPE integer RANGE 0 5",
            "DEFINE cov_dup TYPE integer RANGE 0 10",
            "SETV only_setv 7 TYPE integer RANGE 0 100",
            
            # More expression tests
            "EVAL (+ (* 2 3) (- 10 5))",
            "EVAL (+ 1 2 3)",
            "EVAL (* 1 2 3)",
            "EVAL (if (> 5 3) (+ 1 2) (- 1 2))",
            "EVAL (not (and 1 1))",
            "EVAL (not (or 0 0))",
            
            # More list operations
            "LPUSH multi_1 a b c d e",
            "RPUSH multi_2 1 2 3 4 5",
            "LRANGE multi_1 0 2",
            "LRANGE multi_2 -3 -1",
            "LINDEX multi_1 -1",
            "LREM multi_1 1 a",
            "LREM multi_1 -1 a",
            "LREM multi_1 0 a",
            "LREV multi_1",
            
            # More string operations
            "SET str_test abcdef",
            "APPEND str_test ghij",
            "STRLEN str_test",
            "GETRANGE str_test 0 -1",
            "GETRANGE str_test 1 3",
            "GETRANGE str_test -3 -1",
            
            # Number operation chains
            "SET num_chain 100",
            "INCR num_chain",
            "INCR num_chain",
            "INCR num_chain",
            "DECR num_chain",
            "DECR num_chain",
            "GET num_chain",
            "INCRBY num_chain 50",
            "DECRBY num_chain 25",
            "GET num_chain",
            
            # Nested if
            "EVAL (if (if 1 0 1) 100 200)",
            "EVAL (if (> 10 5) (if (< 5 10) 1 0) 0)",
            
            # Complex expressions
            "EVAL (* (+ 1 2) (+ 3 4))",
            "EVAL (+ (* 2 3) (* 4 5))",
            
            # CALC commands
            "CALC calc_result (+ 10 20)",
            "SET calc_x 5",
            "CALC calc_result (* $calc_x 10)",
            "GET calc_result",

            # More boundary cases
            "EVAL 0",
            "EVAL 1",
            "EVAL -1",
            "EVAL (+ 0 1)",
            "EVAL (- 1 1)",
            "EVAL (* 1 1)",
            "EVAL (/ 1 1)",
            "EVAL (% 1 1)",

            # Negative indexes
            "LPUSH neg_idx a b c",
            "LINDEX neg_idx -1",
            "LINDEX neg_idx -2",
            "LINDEX neg_idx -3",
            "LSET neg_idx -1 last",
            "LRANGE neg_idx -3 -1",

            # Division/modulo boundaries
            "EVAL (/ 100 7)",
            "EVAL (% 100 7)",
            "EVAL (/ -100 7)",
            "EVAL (% -100 7)",

            # Full list operations
            "LPUSH full_lst 1 2 3 4 5",
            "LLEN full_lst",
            "LRANGE full_lst 0 -1",
            "LINDEX full_lst 0",
            "LINDEX full_lst 4",
            "LREV full_lst",
            "LRANGE full_lst 0 -1",

            # MSET MGET full coverage
            "MSET ms1 v1 ms2 v2 ms3 v3 ms4 v4",
            "MGET ms1 ms2 ms3 ms4",
            "MGET ms1 missing ms3",

            # String pattern matching
            'DEFINE p1 TYPE string PATTERN "^[a-z]+$"',
            'DEFINE p2 TYPE string PATTERN "^[0-9]+$"',
            'DEFINE p3 TYPE string PATTERN "^[A-Z]+$"',
            "SET p1_v1 abc", "SET p1_v2 123", "SET p1_v3 Abc",
            "SET p2_v1 123", "SET p2_v2 abc",
            "SET p3_v1 ABC", "SET p3_v2 abc",

            # Enum value tests
            "DEFINE color TYPE enum VALUES red,green,blue",
            "SET color red", "SET color green", "SET color blue",
            "SET color yellow", "SET color red", "SET color RED",

            # Number range boundaries
            "DEFINE range1 TYPE integer RANGE 0 0",
            "DEFINE range2 TYPE integer RANGE 0 1",
            "DEFINE range3 TYPE integer RANGE -1 1",
            "DEFINE range4 TYPE integer RANGE -100 100",
            "SETV r1 0 TYPE integer RANGE 0 0",
            "SETV r2 1 TYPE integer RANGE 0 1",
            "SETV r3 -1 TYPE integer RANGE -1 1",
        ]
        return random.choice(cases)
    
    def generate_error_case():
        """Generate error case tests - trigger various error handling branches"""
        cases = [
            # Missing parameter errors
            "SET",
            "GET",
            "DEL",
            "EXISTS",
            "INCR",
            "DECR",
            "INCRBY",
            "DECRBY",
            "APPEND",
            "STRLEN",
            "GETRANGE",
            "MSET",
            "MGET",
            "LPUSH",
            "RPUSH",
            "LPOP",
            "RPOP",
            "LLEN",
            "LRANGE",
            "LINDEX",
            "LSET",
            "LREM",
            "LREV",
            "EVAL",
            "CALC",
            "DEFINE",
            "SETV",
            "VALIDATE",
            
            # EVAL expression syntax errors
            "EVAL invalid_expr",
            "EVAL (/ 10 0)",
            "EVAL (% 10 0)",
            "EVAL (+ 1)",
            "EVAL (- 1 2 3)",
            "EVAL (* 1 2 3 4)",
            "EVAL (if 1 2)",
            "EVAL (if 1 2 3 4)",
            "EVAL (%)",
            "EVAL (++)",
            "EVAL ()",
            "EVAL ( + 1 2 )",
            "EVAL (and 1)",
            "EVAL (or 0)",
            "EVAL (not)",
            "EVAL (not 1 2)",
            "EVAL (< 1 2 3)",
            "EVAL (> 1 2)",
            "EVAL (== 1)",
            "EVAL (!= 1)",
            
            # Undefined variables
            "EVAL $no_such_var_for_eval",
            "EVAL (+ $undefined_var 1)",
            "CALC calc_var (+ $missing 5)",
            
            # DEFINE parameter errors
            "DEFINE",
            "DEFINE bad",
            "DEFINE bad TYPE",
            "DEFINE bad TYPE integer",
            "DEFINE bad TYPE integer RANGE",
            "DEFINE bad TYPE integer RANGE 5",
            "DEFINE bad TYPE integer RANGE 5 1",  # min > max
            "DEFINE bad TYPE string",
            "DEFINE bad TYPE string PATTERN",
            'DEFINE bad TYPE string PATTERN "',
            "DEFINE bad TYPE enum",
            "DEFINE bad TYPE enum VALUES",
            "DEFINE bad TYPE enum VALUES a",
            "DEFINE bad TYPE unknown",
            
            # SETV parameter errors
            "SETV x",
            "SETV x 1",
            "SETV x 1 TYPE",
            "SETV x 1 TYPE integer",
            "SETV x 1 TYPE integer RANGE",
            "SETV x 1 TYPE integer RANGE 0",
            "SETV v 1 TYPE integer RANGE",
            
            # LSET index errors
            "LSET x",
            "LSET x 0",
            "LSET x 0 v extra",
            "LPUSH lst_err 1", "LSET lst_err -1 v",
            
            # LREM parameter errors
            "LREM x",
            "LREM k 0",
            "LREM k 0 v extra",
            
            # LRANGE parameter errors
            "LRANGE x",
            "LRANGE x 0",
            
            # CALC parameter errors
            "CALC",
            "CALC k",
            "CALC k (+ 1 2) extra",
            
            # Type errors
            "SET num 123", "INCR num",  # assuming numbers can INCR
            
            # Pattern matching errors
            'DEFINE re_err TYPE string PATTERN "***"',  # invalid regex
            'DEFINE re_err2 TYPE string PATTERN "[invalid"',  # invalid regex
            'DEFINE re_err3 TYPE string PATTERN "("',  # invalid regex

            # Duplicate key definitions
            "DEFINE dup_key TYPE integer RANGE 0 10",
            "DEFINE dup_key TYPE integer RANGE 0 20",

            # List operation boundaries
            "LPUSH empty_err 1",
            "LREM empty_err 5 x",  # delete non-existing element
            "LPUSH small_lst a",
            "LINDEX small_lst 1",  # index out of range
            "LINDEX small_lst -2",  # negative index out of range
            "LSET small_lst 5 x",  # LSET index out of range
            "LSET small_lst -2 x",  # LSET negative index out of range

            # String operation boundaries
            "SET short s",
            "GETRANGE short 0 10",  # range out of bounds
            "GETRANGE short -10 -5",  # negative index out of range

            # Number overflow tests
            "SET large 999999",
            "INCRBY large 1",
            "DECRBY large 1",

            # Mixed type operations
            "SET numstr 123",
            "APPEND numstr abc",  # append non-number

            # More SETV errors
            "SETV sv_err",
            "SETV sv_err 1 TYPE",
            "SETV sv_err 1 TYPE integer",
            "SETV sv_err 1 TYPE integer RANGE 0",
            "SETV sv_err 1 TYPE string",
            "SETV sv_err 1 TYPE string PATTERN",
            "SETV sv_err 1 TYPE enum",
            "SETV sv_err 1 TYPE enum VALUES",

            # More VALIDATE errors
            "VALIDATE",  # no key name
            "VALIDATE undefined_key",

            # More CALC errors
            "CALC",  # no arguments
            "CALC calc",  # no expression
            "CALC calc 123",  # no parentheses

            # Complex nested expression errors
            "EVAL (if 1)",  # missing branches
            "EVAL (if)",  # missing all parameters
            "EVAL (and)",  # missing parameters
            "EVAL (or)",  # missing parameters
            "EVAL (not 1 2)",  # too many parameters

            # Variable reference errors
            "EVAL $",
            "CALC c (+ $ $)",
        ]
        return random.choice(cases)
    
    def generate_mixed_sequence():
        """Generate mixed operation sequences"""
        seq = []
        for _ in range(random.randint(2, 5)):
            cmd_type = random.choice(["string", "list", "expr", "validation"])
            if cmd_type == "string":
                seq.append(generate_string_command())
            elif cmd_type == "list":
                seq.append(generate_list_command())
            elif cmd_type == "expr":
                seq.append(generate_expression_command())
            else:
                seq.append(generate_validation_command())
        return seq
    
    # Fixed order: contains variable/list dependencies, no shuffle
    # Ensure coverage of all key branches, increase expression and validation ratio
    prefix_pool = [
        # String operations - basic
        "SET s1 hello",
        "GET s1",
        "SET s2 world",
        "GET s2",
        "DEL s1",
        "DEL s1 s2",
        "EXISTS s1",
        "EXISTS s1 s2",
        
        # String operations - numbers
        "SET num 100",
        "INCR num",
        "DECR num",
        "INCRBY num 5",
        "DECRBY num 3",
        "GET num",
        
        # String operations - append
        "SET app test",
        "APPEND app end",
        "STRLEN app",
        "GET app",
        
        # String operations - GETRANGE
        "SET rng hello",
        "GETRANGE rng 0 2",
        "GETRANGE rng -3 -1",
        "GETRANGE rng 0 -1",
        "GETRANGE rng 10 20",
        "GETRANGE rng 2 1",
        
        # String operations - MSET/MGET
        "MSET m1 a m2 b m3 c",
        "MGET m1 m2 m3",
        "MGET m1 missing m2",
        "GET m1",
        
        # List operations - basic
        "LPUSH lst1 a b c",
        "RPUSH lst1 d e f",
        "LLEN lst1",
        "LRANGE lst1 0 -1",
        "LPOP lst1",
        "RPOP lst1",
        
        # List operations - index
        "LPUSH lst2 1 2 3",
        "LINDEX lst2 0",
        "LINDEX lst2 -1",
        "LINDEX lst2 10",
        "LSET lst2 0 first",
        
        # List operations - LREM
        "LPUSH lst3 a b a c a",
        "LREM lst3 0 a",
        "LREM lst3 1 a",
        "LREM lst3 -1 a",
        "LLEN lst3",
        
        # List operations - LREV
        "LPUSH lst4 1 2 3",
        "LREV lst4",
        "LRANGE lst4 0 -1",
        "LREV lst4",
        "LRANGE lst4 0 -1",
        
        # ============ Expression operations - Key coverage ============
        # Arithmetic operations
        "EVAL (+ 10 20)",
        "EVAL (- 100 50)",
        "EVAL (* 6 7)",
        "EVAL (/ 100 3)",
        "EVAL (% 17 5)",
        
        # Division by zero - critical!
        "EVAL (/ 1 0)",
        "EVAL (/ 0 1)",
        "EVAL (% 10 0)",
        "EVAL (% 0 5)",
        
        # Boundary values
        "EVAL (+ 0 0)",
        "EVAL (- 0 0)",
        "EVAL (* 0 100)",
        "EVAL (/ 100 100)",
        "EVAL (% 100 100)",
        
        # Negative number operations
        "EVAL (- 0 5)",
        "EVAL (+ -5 5)",
        "EVAL (* -2 -3)",
        "EVAL (- -10 -5)",
        "EVAL (/ -10 2)",
        "EVAL (% -10 3)",
        
        # Comparison operations
        "EVAL (< 5 10)",
        "EVAL (> 10 5)",
        "EVAL (<= 5 5)",
        "EVAL (>= 5 5)",
        "EVAL (== 5 5)",
        "EVAL (!= 5 3)",
        "EVAL (< -5 -1)",
        "EVAL (> -5 0)",
        
        # Logical operations
        "EVAL (and 1 1)",
        "EVAL (and 0 1)",
        "EVAL (and 0 0)",
        "EVAL (or 0 0)",
        "EVAL (or 0 1)",
        "EVAL (or 1 1)",
        "EVAL (not 0)",
        "EVAL (not 1)",
        
        # Mixed logical
        "EVAL (and (or 0 1) (not 0))",
        "EVAL (or (and 1 1) (not 0))",
        "EVAL (not (and 1 0))",
        "EVAL (not (or 0 0))",
        
        # if expressions
        "EVAL (if 1 100 200)",
        "EVAL (if 0 100 200)",
        "EVAL (if (< 5 10) 1 0)",
        "EVAL (if (> 5 10) 1 0)",
        "EVAL (if (== 1 1) 1 0)",
        "EVAL (if (and 1 1) (+ 1 2) (+ 3 4))",
        
        # Nested if
        "EVAL (if (if 1 0 1) 100 200)",
        "EVAL (if (if 0 1 0) 100 200)",
        "EVAL (if (if (< 5 10) 1 0) 100 200)",
        
        # Nested expressions
        "EVAL (+ (* 2 3) (- 10 5))",
        "EVAL (* (+ 1 2) (+ 3 4))",
        "EVAL (+ (* 2 3) (* 4 5))",
        "EVAL (if (> (+ 1 2) 3) (+ 1 2) 0)",
        "EVAL (* (+ 1 2) (- 10 5))",
        
        # Multi-argument - possible error branches
        "EVAL (+ 1 2 3 4 5)",
        "EVAL (* 1 2 3)",
        "EVAL (- 10 5 3)",
        "EVAL (+ 1 2 3)",
        
        # Variable references - key tests
        "SET x0 10",
        "SET x1 20",
        "SET x2 -5",
        "EVAL (+ $x0 $x1)",
        "EVAL (* $x0 $x1)",
        "EVAL (+ $x0 $x0 $x0)",
        "EVAL (+ $x0 $x2)",
        "CALC calc1 (+ $x0 5)",
        "GET calc1",
        "CALC calc2 (* $x1 $x2)",
        "GET calc2",
        
        # ============ Validation operations - Key coverage ============
        # integer type
        "DEFINE v_int TYPE integer RANGE 0 100",
        "SET v_int 50",
        "SET v_int 0",
        "SET v_int 100",
        "SET v_int -1",
        "SET v_int 101",
        "VALIDATE v_int",
        
        # integer negative range
        "DEFINE v_neg TYPE integer RANGE -50 50",
        "SET v_neg -50",
        "SET v_neg 0",
        "SET v_neg 50",
        "SET v_neg -51",
        "SET v_neg 51",
        
        # string type - multiple patterns
        'DEFINE v_str TYPE string PATTERN "^[a-z]+$"',
        "SETV v_str1 test TYPE string PATTERN \"^[a-z]+$\"",
        'SET v_str abc',
        'SET v_str ABC',
        'SET v_str 123',
        'SET v_str a1b2',
        'VALIDATE v_str',
        
        'DEFINE v_str2 TYPE string PATTERN "^[0-9]+$"',
        "SETV v_numstr 123 TYPE string PATTERN \"^[0-9]+$\"",
        "SET v_str2 123",
        "SET v_str2 abc",
        
        # enum type
        "DEFINE v_enum TYPE enum VALUES active,inactive,pending",
        "SETV v_enum1 active TYPE enum VALUES active,inactive,pending",
        "SET v_enum active",
        "SET v_enum inactive",
        "SET v_enum unknown",
        "VALIDATE v_enum",
        
        # SETV inline validation
        "SETV sv_int 50 TYPE integer RANGE 0 100",
        "SETV sv_int -1 TYPE integer RANGE 0 100",
        "SETV sv_int 101 TYPE integer RANGE 0 100",
        "SETV sv_str ok TYPE string PATTERN \"^[a-z]+$\"",
        "SETV sv_str FAIL TYPE string PATTERN \"^[a-z]+$\"",
        "SETV sv_enum ok TYPE enum VALUES a,b,c",
        "SETV sv_enum bad TYPE enum VALUES a,b,c",
        
        # Complex combinations
        "SET s10 a", "APPEND s10 b", "APPEND s10 c", "STRLEN s10",
        "LPUSH l10 1 2", "LPOP l10", "LPOP l10", "LLEN l10",
        "SET n10 5", "INCR n10", "DECR n10", "INCRBY n10 10", "GET n10",
        "DEFINE v10 TYPE integer RANGE 0 10", "SETV v10 5 TYPE integer RANGE 0 10", "VALIDATE v10",
        
        # More expression error cases
        "EVAL $undefined_var",
        "EVAL (+ $undefined 1)",
        "CALC cv (+ $missing 5)",
        "EVAL (+ 1)",
        "EVAL (- 1 2 3)",
        "EVAL (if 1 2)",
        "EVAL (if 1 2 3 4)",
        "EVAL (%)",
        "EVAL ()",
        "EVAL (and 1)",
        "EVAL (or 0)",
        "EVAL (not)",
        "EVAL (not 1 2)",
    ]
    k_prefix = min(len(prefix_pool), max(0, num_cases // 3))
    commands.extend(prefix_pool[:k_prefix])
    
    while len(commands) < num_cases:
        choice = random.random()
        if choice < 0.18:
            commands.append(generate_string_command())
        elif choice < 0.32:
            commands.append(generate_list_command())
        elif choice < 0.50:
            commands.append(generate_expression_command())
        elif choice < 0.65:
            commands.append(generate_validation_command())
        elif choice < 0.80:
            commands.append(generate_edge_case())
        elif choice < 0.93:
            commands.append(generate_error_case())
        else:
            seq = generate_mixed_sequence()
            for c in seq[:4]:
                if len(commands) >= num_cases:
                    break
                commands.append(c)
    
    return commands[:num_cases]


def metamorphic_relations() -> list[tuple]:
    """
    Define metamorphic testing relations.
    
    Returns:
        [(sequence1, sequence2, relation), ...]
        relation: "EQ" means final outputs should be equal, "NE" means they should differ
    
    Critical Rules:
    1. Each sequence runs in a fresh MiniRedis instance (no shared state)
    2. Only the last command's output from each sequence is compared
    3. Relations must hold on the ORIGINAL program (invalid MRs are discarded)
    """
    relations = []
    
    # ============ STRING OPERATIONS - Simple and Reliable ============
    
    # INCR/DECR cancellation - most reliable
    relations.append((["SET x 100", "GET x"], ["SET x 100", "INCR x", "DECR x", "GET x"], "EQ"))
    relations.append((["SET x 0", "INCR x", "INCR x", "DECR x", "DECR x", "GET x"], ["SET x 0"], "EQ"))
    relations.append((["SET x 50", "INCR x", "GET x"], ["SET x 51"], "EQ"))
    relations.append((["SET x 50", "DECR x", "GET x"], ["SET x 49"], "EQ"))
    relations.append((["SET x 10", "INCRBY x 5", "GET x"], ["SET x 15"], "EQ"))
    relations.append((["SET x 10", "DECRBY x 3", "GET x"], ["SET x 7"], "EQ"))
    
    # INCR/DECR on non-existent keys
    relations.append((["INCR newkey", "GET newkey"], ["SET newkey 1", "GET newkey"], "EQ"))
    relations.append((["DECR newkey", "GET newkey"], ["SET newkey -1", "GET newkey"], "EQ"))
    
    # Multiple operations
    relations.append((["SET x 0", "INCR x", "INCR x", "INCR x", "GET x"], ["SET x 3"], "EQ"))
    relations.append((["SET x 0", "DECR x", "DECR x", "DECR x", "GET x"], ["SET x -3"], "EQ"))
    relations.append((["SET x 10", "INCRBY x 5", "DECRBY x 3", "GET x"], ["SET x 12"], "EQ"))
    
    # DEL operations
    relations.append((["SET k1 v1", "DEL k1", "EXISTS k1"], ["EXISTS missing"], "EQ"))
    relations.append((["DEL nonexistent"], ["DEL x"], "EQ"))
    relations.append((["SET k1 v1", "SET k2 v2", "DEL k1 k2"], ["SET k1 v1", "DEL k1"], "NE"))
    
    # EXISTS operations
    relations.append((["SET k1 v1", "EXISTS k1 k2"], ["SET k1 v1", "EXISTS k1"], "NE"))
    relations.append((["SET k1 v1", "DEL k1", "EXISTS k1"], ["EXISTS missing"], "EQ"))
    
    # STRLEN operations
    relations.append((["SET s abc", "STRLEN s"], ["SET s ab", "APPEND s c", "STRLEN s"], "EQ"))
    relations.append((["STRLEN missing"], ["STRLEN empty"], "EQ"))
    relations.append((["SET s abc", "STRLEN s"], ["SET s xyz", "STRLEN s"], "NE"))
    
    # APPEND operations
    relations.append((["SET s hello", "APPEND s world", "GET s"], ["SET s helloworld"], "EQ"))
    relations.append((["SET s a", "APPEND s b", "APPEND s c", "GET s"], ["SET s abc"], "EQ"))
    relations.append((["SET s hello", "APPEND s world", "STRLEN s"], ["SET s helloworld", "STRLEN s"], "EQ"))
    
    # GETRANGE operations
    relations.append((["SET s hello", "GETRANGE s 0 4"], ["GET s"], "EQ"))
    relations.append((["SET s hello", "GETRANGE s 0 -1"], ["GET s"], "EQ"))
    relations.append((["SET s abc", "GETRANGE s 0 0"], ["SET s a"], "EQ"))
    relations.append((["SET s abc", "GETRANGE s 0 100"], ["GET s"], "EQ"))
    
    # MSET/MGET operations
    relations.append((["MSET k1 v1 k2 v2", "GET k1"], ["SET k1 v1", "GET k1"], "EQ"))
    relations.append((["MSET k1 v1 k2 v2", "MGET k1 k2"], ["SET k1 v1", "SET k2 v2", "MGET k1 k2"], "EQ"))
    
    # ============ LIST OPERATIONS ============
    
    # LPUSH/RPUSH length
    relations.append((["LPUSH lst a b c", "LLEN lst"], ["SET x 3"], "EQ"))
    relations.append((["LPUSH lst 1 2 3", "LLEN lst"], ["RPUSH lst 3 2 1", "LLEN lst"], "EQ"))
    
    # LPOP/RPOP
    relations.append((["LPUSH lst a b c", "LPOP lst"], ["SET x c"], "EQ"))
    relations.append((["LPUSH lst a b c", "RPOP lst"], ["SET x a"], "EQ"))
    relations.append((["LPOP missing"], ["RPOP missing"], "EQ"))
    
    # LLEN
    relations.append((["LPUSH lst a", "LLEN lst"], ["LLEN missing"], "NE"))
    relations.append((["SET not_list abc", "LLEN not_list"], ["LLEN missing"], "EQ"))
    
    # LRANGE
    relations.append((["LPUSH lst a b c", "LRANGE lst 0 0"], ["LPUSH lst a b c", "LINDEX lst 0"], "EQ"))
    relations.append((["LPUSH lst a b c", "LRANGE lst 0 100"], ["LPUSH lst a b c", "LRANGE lst 0 -1"], "EQ"))
    relations.append((["LPUSH lst a b c", "LRANGE lst 0 1"], ["LPUSH lst x y z", "LRANGE lst 0 1"], "NE"))
    
    # LINDEX
    relations.append((["LPUSH lst 1 2 3", "LINDEX lst 0"], ["SET x 1"], "EQ"))
    relations.append((["LPUSH lst 1 2 3", "LINDEX lst -1"], ["LPUSH lst 1 2 3", "LINDEX lst 2"], "EQ"))
    relations.append((["LPUSH lst 1 2 3", "LINDEX lst 100"], ["LPUSH lst 1 2 3", "LINDEX lst -100"], "EQ"))
    
    # LSET
    relations.append((["LPUSH lst a b c", "LSET lst 0 x", "LINDEX lst 0"], ["SET x x"], "EQ"))
    relations.append((["LPUSH lst a b c", "LSET lst 0 x", "LINDEX lst 1"], ["SET x b"], "EQ"))
    
    # LREM
    relations.append((["LPUSH lst a b a c a", "LREM lst 0 a", "LLEN lst"], ["LPUSH lst b c", "LLEN lst"], "EQ"))
    relations.append((["LPUSH lst a b a", "LREM lst 1 a", "LLEN lst"], ["LPUSH lst b a", "LLEN lst"], "EQ"))
    relations.append((["LPUSH lst a b a", "LREM lst -1 a", "LLEN lst"], ["LPUSH lst a b", "LLEN lst"], "EQ"))
    
    # LREV
    relations.append((["LPUSH lst 1 2 3", "LREV lst", "LLEN lst"], ["LPUSH lst 1 2 3", "LLEN lst"], "EQ"))
    relations.append((["LPUSH lst 1 2 3", "LREV lst", "LREV lst", "LRANGE lst 0 -1"], ["LPUSH lst 1 2 3", "LRANGE lst 0 -1"], "EQ"))
    
    # ============ EXPRESSION OPERATIONS ============
    
    # Basic arithmetic
    relations.append((["EVAL (+ 10 20)"], ["EVAL 30"], "EQ"))
    relations.append((["EVAL (- 100 25)"], ["EVAL 75"], "EQ"))
    relations.append((["EVAL (* 6 7)"], ["EVAL 42"], "EQ"))
    relations.append((["EVAL (/ 100 3)"], ["EVAL 33"], "EQ"))
    relations.append((["EVAL (% 17 5)"], ["EVAL 2"], "EQ"))
    
    # Arithmetic with negatives
    relations.append((["EVAL (- 0 5)"], ["EVAL -5"], "EQ"))
    relations.append((["EVAL (+ -5 5)"], ["EVAL 0"], "EQ"))
    relations.append((["EVAL (* -2 3)"], ["EVAL -6"], "EQ"))
    relations.append((["EVAL (/ -10 2)"], ["EVAL -5"], "EQ"))
    
    # Commutative property
    relations.append((["EVAL (+ 3 5)"], ["EVAL (+ 5 3)"], "EQ"))
    relations.append((["EVAL (* 3 7)"], ["EVAL (* 7 3)"], "EQ"))
    
    # Comparison operations
    relations.append((["EVAL (< 5 10)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (> 10 5)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (<= 5 5)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (>= 5 5)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (== 5 5)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (!= 5 3)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (< 10 5)"], ["EVAL 0"], "EQ"))
    
    # Logical operations
    relations.append((["EVAL (and 1 1)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (and 1 0)"], ["EVAL 0"], "EQ"))
    relations.append((["EVAL (or 0 0)"], ["EVAL 0"], "EQ"))
    relations.append((["EVAL (or 0 1)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (not 0)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (not 1)"], ["EVAL 0"], "EQ"))
    
    # De Morgan's law
    relations.append((["EVAL (not (and 1 0))"], ["EVAL (or (not 1) (not 0))"], "EQ"))
    relations.append((["EVAL (not (or 0 0))"], ["EVAL (and (not 0) (not 0))"], "EQ"))
    
    # Double negation
    relations.append((["EVAL (not (not 1))"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (not (not 0))"], ["EVAL 0"], "EQ"))
    
    # if expressions
    relations.append((["EVAL (if 1 100 200)"], ["EVAL 100"], "EQ"))
    relations.append((["EVAL (if 0 100 200)"], ["EVAL 200"], "EQ"))
    relations.append((["EVAL (if (< 5 10) 1 0)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (if (> 5 10) 1 0)"], ["EVAL 0"], "EQ"))
    
    # Nested if
    relations.append((["EVAL (if (if 1 0 1) 100 200)"], ["EVAL 200"], "EQ"))
    relations.append((["EVAL (if (if 0 1 0) 100 200)"], ["EVAL 100"], "EQ"))
    relations.append((["EVAL (if (and 1 1) 100 200)"], ["EVAL 100"], "EQ"))
    
    # Nested expressions
    relations.append((["EVAL (+ (* 2 3) (- 10 5))"], ["EVAL 11"], "EQ"))
    relations.append((["EVAL (* (+ 1 2) (+ 3 4))"], ["EVAL 21"], "EQ"))
    
    # Variable references
    relations.append((["SET x 10", "EVAL (+ $x 5)"], ["EVAL 15"], "EQ"))
    relations.append((["SET x 10", "SET y 20", "EVAL (+ $x $y)"], ["EVAL 30"], "EQ"))
    relations.append((["SET x 5", "EVAL (+ $x $x $x)"], ["EVAL 15"], "EQ"))
    
    # CALC operations
    relations.append((["CALC r (+ 10 20)", "GET r"], ["SET r 30", "GET r"], "EQ"))
    relations.append((["SET x 5", "CALC r (+ $x 10)", "GET r"], ["SET r 15", "GET r"], "EQ"))
    
    # ============ VALIDATION OPERATIONS ============
    
    # Integer range
    relations.append((["DEFINE age TYPE integer RANGE 0 150", "SET age 25"], ["SET age 25"], "EQ"))
    relations.append((["DEFINE age TYPE integer RANGE 0 150", "SET age 200"], ["DEFINE age TYPE integer RANGE 0 150", "SETV age 200 TYPE integer RANGE 0 150"], "EQ"))
    relations.append((["SETV x 50 TYPE integer RANGE 0 100"], ["SET x 50"], "EQ"))
    
    # VALIDATE behavior
    relations.append((["DEFINE x TYPE integer RANGE 0 100", "SET x 50", "VALIDATE x"], ["DEFINE x TYPE integer RANGE 0 100", "SET x 50"], "NE"))
    relations.append((["DEFINE x TYPE integer RANGE 0 100", "SETV x 50 TYPE integer RANGE 0 100", "VALIDATE x"], ["DEFINE x TYPE integer RANGE 0 100", "SETV x 50 TYPE integer RANGE 0 100"], "NE"))
    relations.append((["VALIDATE missing"], ["SET x 1", "VALIDATE x"], "EQ"))
    
    # String pattern
    relations.append((['DEFINE email TYPE string PATTERN "^[a-z]+$"', 'SET email test'], ["SET email test"], "EQ"))
    relations.append((['DEFINE email TYPE string PATTERN "^[a-z]+$"', 'SET email 123'], ["SET email 123"], "NE"))
    
    # Enum
    relations.append((["DEFINE status TYPE enum VALUES a,b,c", "SET status a"], ["SET status a"], "EQ"))
    relations.append((["DEFINE status TYPE enum VALUES a,b,c", "SET status x"], ["SET status x"], "NE"))
    
    # ============ ERROR HANDLING ============
    
    # Division by zero
    relations.append((["EVAL (/ 1 0)"], ["EVAL (/ 5 0)"], "EQ"))
    relations.append((["EVAL (% 1 0)"], ["EVAL (% 10 0)"], "EQ"))
    
    # Out of range
    relations.append((["LPUSH lst 1 2", "LINDEX lst 100"], ["LPUSH lst 1 2", "LINDEX lst -100"], "EQ"))
    
    # Non-existent key
    relations.append((["GET missing"], ["LPOP missing"], "EQ"))
    
    # ============ ADDITIONAL RELIABLE MRs ============
    
    # LREV equivalence
    relations.append((["LPUSH lst 1 2 3", "LREV lst", "LRANGE lst 0 -1"], ["RPUSH lst 3 2 1", "LRANGE lst 0 -1"], "EQ"))
    
    # Empty list
    relations.append((["LPUSH empty 1", "LPOP empty", "LLEN empty"], ["SET x 0"], "EQ"))
    
    # Zero operations
    relations.append((["SET x 0", "GET x"], ["SET x 0"], "EQ"))
    relations.append((["EVAL (/ 0 100)"], ["EVAL 0"], "EQ"))
    relations.append((["EVAL (* 0 100)"], ["EVAL 0"], "EQ"))
    
    # String vs number
    relations.append((["SET x 123", "GET x"], ["SET x abc", "GET x"], "NE"))
    
    # LPUSH order
    relations.append((["LPUSH lst a b c", "LPOP lst"], ["LPUSH lst a b c", "RPOP lst"], "NE"))
    
    # EXISTS different counts
    relations.append((["SET k1 v1", "EXISTS k1 k2"], ["SET k1 v1", "EXISTS k1 k2 k3"], "NE"))
    
    # DEL different counts
    relations.append((["SET k1 v1", "SET k2 v2", "DEL k1 k2"], ["SET k1 v1", "DEL k1"], "NE"))
    
    # GETRANGE different
    relations.append((["SET s abc", "GETRANGE s 0 0"], ["SET s abc", "GETRANGE s 1 1"], "NE"))
    
    # LLEN different
    relations.append((["LPUSH lst a b", "LLEN lst"], ["LPUSH lst a", "LLEN lst"], "NE"))
    
    # LINDEX different positions
    relations.append((["LPUSH lst a b c", "LINDEX lst 0"], ["LPUSH lst a b c", "LINDEX lst 2"], "NE"))
    
    # CALC chain
    relations.append((["CALC r (+ 1 2)", "CALC r (+ $r 3)", "CALC r (+ $r 4)", "GET r"], ["CALC ref (+ 1 2 3 4)", "GET ref"], "EQ"))
    
    # Nested arithmetic
    relations.append((["EVAL (+ (- 10 5) (* 2 3))"], ["EVAL 11"], "EQ"))
    relations.append((["EVAL (* (+ 1 2) (- 10 5))"], ["EVAL 15"], "EQ"))
    
    # Modulo
    relations.append((["EVAL (% 10 3)"], ["EVAL 1"], "EQ"))
    relations.append((["EVAL (/ 10 3)"], ["EVAL 3"], "EQ"))
    
    # Comparison result types
    relations.append((["EVAL (< 5 10)"], ["EVAL (> 5 10)"], "NE"))
    relations.append((["EVAL (== 5 5)"], ["EVAL (!= 5 5)"], "NE"))
    
    # Logic result types
    relations.append((["EVAL (and 1 1)"], ["EVAL (or 0 0)"], "NE"))
    
    # Boundary conditions
    relations.append((["DEFINE x TYPE integer RANGE 0 100", "SETV x 0 TYPE integer RANGE 0 100"], ["DEFINE x TYPE integer RANGE 0 100", "SETV x 100 TYPE integer RANGE 0 100"], "EQ"))
    relations.append((["DEFINE x TYPE integer RANGE 0 100", "SETV x 0 TYPE integer RANGE 0 100", "VALIDATE x"], ["DEFINE x TYPE integer RANGE 0 100", "SETV x 150 TYPE integer RANGE 0 100", "VALIDATE x"], "NE"))
    
    relations.append((
        ["SET counter 50", "GET counter"],
        ["SET counter 50", "INCRBY counter 10", "DECRBY counter 10", "GET counter"],
        "EQ"
    ))
    
    relations.append((
        ["SET x 0", "GET x"],
        ["SET x 0", "INCR x", "INCR x", "INCR x", "DECR x", "DECR x", "DECR x", "GET x"],
        "EQ"
    ))
    
    # 4-5. String length equivalence
    relations.append((
        ["SET s abc", "STRLEN s"],
        ["SET s ab", "APPEND s c", "STRLEN s"],
        "EQ"
    ))
    
    relations.append((
        ["SET s1 a", "SET s2 ab", "SET s3 abc"],
        ["APPEND s1 bc", "APPEND s2 c", "STRLEN s1"],
        "NE"
    ))
    
    # 6-7. MSET vs separate SET
    relations.append((
        ["SET k1 v1", "SET k2 v2", "GET k1"],
        ["MSET k1 v1 k2 v2", "GET k1"],
        "EQ"
    ))
    
    relations.append((
        ["MSET k1 v1 k2 v2", "MGET k1 k2"],
        ["SET k1 v1", "SET k2 v2", "MGET k1 k2"],
        "EQ"
    ))
    
    # 8-9. DEL behavior
    relations.append((
        ["SET k1 v1", "SET k2 v2", "EXISTS k1 k2"],
        ["SET k1 v1", "DEL k1", "EXISTS k1 k2"],
        "NE"
    ))
    
    relations.append((
        ["SET x 1", "DEL x", "DEL x", "GET x"],
        ["SET x 1", "DEL x", "GET x"],
        "EQ"
    ))
    
    # 10-11. EXISTS behavior
    relations.append((
        ["EXISTS no_such_key"],
        ["SET has_key value", "EXISTS has_key"],
        "NE"
    ))
    
    relations.append((
        ["SET k 1", "DEL k", "EXISTS k"],
        ["EXISTS k"],
        "EQ"
    ))
    
    # 12-13. GETRANGE behavior
    relations.append((
        ["SET r test", "GETRANGE r 0 3"],
        ["SET r test", "GET r"],
        "NE"
    ))
    
    relations.append((
        ["SET r hello", "GETRANGE r 0 -1"],
        ["GET r"],
        "NE"
    ))
    
    # ============ List Command Metamorphic Relations ============
    
    # 14-15. LPUSH/RPUSH order
    relations.append((
        ["LPUSH lst a b c", "LPOP lst"],
        ["LPUSH lst a b c", "RPOP lst"],
        "NE"
    ))
    
    relations.append((
        ["LPUSH order a b c", "LRANGE order 0 -1"],
        ["RPUSH order c b a", "LRANGE order 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH llen_test 1 2 3", "LLEN llen_test"],
        ["RPUSH llen_test 1 2 3", "LLEN llen_test"],
        "EQ"
    ))
    
    relations.append((
        ["LPUSH llen_test 1", "LLEN llen_test"],
        ["LLEN empty_llen"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH lset_test 1 2 3", "LSET lset_test 0 new", "LINDEX lset_test 0"],
        ["LPUSH lset_test 1 2 3", "LINDEX lset_test 0"],
        "NE"
    ))
    
    relations.append((
        ["LPUSH lidx_test 1 2 3", "LINDEX lidx_test -1"],
        ["LPUSH lidx_test 1 2 3", "LINDEX lidx_test 2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lr_test 1 2 3", "LRANGE lr_test 0 -1"],
        ["LPUSH lr_test 1 2 3", "LLEN lr_test"],
        "NE"
    ))
    
    relations.append((
        ["LPUSH lr_test 1 2 3", "LRANGE lr_test 0 2"],
        ["LPUSH lr_test 1 2 3", "LRANGE lr_test 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rem_all a b a c a", "LREM rem_all 0 a", "LLEN rem_all"],
        ["LPUSH rem_all b c", "LLEN rem_all"],
        "EQ"
    ))
    
    relations.append((
        ["LPUSH rem_dir a b a", "LREM rem_dir 1 a", "LLEN rem_dir"],
        ["LPUSH rem_dir a b a", "LREM rem_dir -1 a", "LLEN rem_dir"],
        "NE"
    ))
    
    relations.append((
        ["LPUSH rem_empty a b c", "LREM rem_empty 0 x", "LLEN rem_empty"],
        ["LPUSH rem_empty a b c", "LLEN rem_empty"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rev_test 1 2 3", "LREV rev_test", "LREV rev_test", "LRANGE rev_test 0 -1"],
        ["LPUSH rev_test 1 2 3", "LRANGE rev_test 0 -1"],
        "EQ"
    ))
    
    relations.append((
        ["LPUSH rev_test2 1 2 3", "LREV rev_test2", "LRANGE rev_test2 0 -1"],
        ["LPUSH rev_test2 1 2 3", "LRANGE rev_test2 0 -1"],
        "NE"
    ))
    

    relations.append((
        ["LPOP empty_list"],
        ["RPOP empty_list"],
        "EQ"
    ))
    

    

    relations.append((
        ["EVAL (+ 10 20)"],
        ["EVAL (+ 20 10)"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (* 6 7)"],
        ["EVAL (* 7 6)"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (+ (* 2 3) 4)"],
        ["EVAL (+ 6 4)"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (* (+ 1 2) (+ 3 4))"],
        ["EVAL (* 3 7)"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (- 10 3)"],
        ["EVAL (+ 10 (* -1 3))"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 10 3)"],
        ["EVAL 3"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (% 17 5)"],
        ["EVAL 2"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (/ 100 10)"],
        ["EVAL 10"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (/ 10 3)"],
        ["EVAL (/ 11 3)"],
        "NE"
    ))
    

    relations.append((
        ["EVAL (< 5 10)"],
        ["EVAL 1"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (> 10 5)"],
        ["EVAL 1"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (< 10 5)"],
        ["EVAL 0"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (< 1 2)"],
        ["EVAL (> 2 1)"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (not 0)"],
        ["EVAL 1"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (and 1 1)"],
        ["EVAL (or 0 1)"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (not (and 1 0))"],
        ["EVAL (or (not 1) (not 0))"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (not (or 0 0))"],
        ["EVAL (and (not 0) (not 0))"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (not (not 1))"],
        ["EVAL 1"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (not (not 0))"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if 1 100 200)"],
        ["EVAL 100"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (if 0 100 200)"],
        ["EVAL 200"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (if (if 1 0 1) 100 200)"],
        ["EVAL 200"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (if (if 0 1 0) 100 200)"],
        ["EVAL 100"],
        "EQ"
    ))
    

    relations.append((
        ["SET x 10", "EVAL (+ $x 5)"],
        ["EVAL 15"],
        "EQ"
    ))
    
    relations.append((
        ["SET x 10", "SET y 20", "EVAL (+ $x $y)"],
        ["EVAL 30"],
        "EQ"
    ))
    
    relations.append((
        ["SET x 5", "EVAL (+ $x $x $x)"],
        ["EVAL 15"],
        "EQ"
    ))
    
    relations.append((
        ["CALC calc_var (+ 25 25)", "GET calc_var"],
        ["SET calc_var 50", "GET calc_var"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (> 10 5) (+ 1 2) (+ 3 4))"],
        ["EVAL 3"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (+ (* 2 3) (- 10 5))"],
        ["EVAL 11"],
        "EQ"
    ))
    

    

    relations.append((
        ["DEFINE age TYPE integer RANGE 0 150", "SET age 25"],
        ["SETV age 25 TYPE integer RANGE 0 150"],
        "EQ"
    ))
    
    relations.append((
        ["DEFINE score TYPE integer RANGE 0 100", "SET score 150"],
        ["DEFINE score TYPE integer RANGE 0 100", "SETV score 150 TYPE integer RANGE 0 100"],
        "EQ"
    ))
    
    relations.append((
        ["DEFINE status TYPE enum VALUES active,inactive,pending", "SET status active"],
        ["SETV status active TYPE enum VALUES active,inactive,pending"],
        "EQ"
    ))
    
    relations.append((
        ['DEFINE email TYPE string PATTERN "^[a-z]+$"', 'SET email test'],
        ['SETV email test TYPE string PATTERN "^[a-z]+$"'],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE val TYPE integer RANGE 0 100", "SET val 50", "VALIDATE val"],
        ["DEFINE val TYPE integer RANGE 0 100", "SET val 200", "VALIDATE val"],
        "NE"
    ))
    
    relations.append((
        ["DEFINE val TYPE integer RANGE 0 100", "SETV val 50 TYPE integer RANGE 0 100", "VALIDATE val", "VALIDATE val"],
        ["DEFINE val TYPE integer RANGE 0 100", "SETV val 50 TYPE integer RANGE 0 100", "VALIDATE val"],
        "EQ"
    ))
    
    relations.append((
        ["DEFINE val TYPE integer RANGE 0 100", "SET val 50", "VALIDATE val"],
        ["DEFINE val TYPE integer RANGE 0 100", "SET val 50"],
        "NE"
    ))
    

    relations.append((
        ["DEFINE en TYPE enum VALUES a,b,c", "SET en a"],
        ["DEFINE en TYPE enum VALUES a,b,c", "SET en invalid"],
        "NE"
    ))
    
    relations.append((
        ["DEFINE en TYPE enum VALUES a,b,c", "SETV en b TYPE enum VALUES a,b,c"],
        ["DEFINE en TYPE enum VALUES a,b,c", "SETV en c TYPE enum VALUES a,b,c"],
        "NE"
    ))
    
    relations.append((
        ['DEFINE re TYPE string PATTERN "^[0-9]+$"', "SETV re 123 TYPE string PATTERN \"^[0-9]+$\""],
        ['DEFINE re TYPE string PATTERN "^[0-9]+$"', "SETV re abc TYPE string PATTERN \"^[0-9]+$\""],
        "NE"
    ))
    

    

    relations.append((
        ["EVAL (/ 1 0)"],
        ["EVAL (% 1 0)"],
        "EQ"
    ))
    
    relations.append((
        ["LPUSH oob_test 1", "LINDEX oob_test 100"],
        ["LPUSH oob_test 1", "LINDEX oob_test -100"],
        "EQ"
    ))
    
    relations.append((
        ["LPOP cross_nil"],
        ["GET cross_nil"],
        "EQ"
    ))
    
    relations.append((
        ["SET nonexistent", "GET nonexistent"],
        ["GET nonexistent"],
        "EQ"
    ))
    

    

    relations.append((
        ["SET num 100", "INCR num", "DECR num"],
        ["SET num 100"],
        "NE"
    ))
    
    relations.append((
        ["SET num 0", "INCRBY num 5", "DECRBY num 2"],
        ["SET num 3"],
        "EQ"
    ))
    
    relations.append((
        ["LPUSH pop_chain 1", "LPOP pop_chain", "LPOP pop_chain"],
        ["RPUSH pop_chain 1", "RPOP pop_chain", "RPOP pop_chain"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (+ 0 0)"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH cross_len 1 2 3", "LLEN cross_len"],
        ["SET cross_len 123", "STRLEN cross_len"],
        "EQ"
    ))
    
    relations.append((
        ["SET var_test 99", "EVAL $var_test"],
        ["EVAL 99"],
        "EQ"
    ))
    
    relations.append((
        ["SET append_eq x", "APPEND append_eq yz", "GET append_eq"],
        ["SET append_eq xyz"],
        "NE"
    ))
    
    relations.append((
        ["SET len_test hi", "STRLEN len_test"],
        ["SET len_test hi", "APPEND len_test bye", "STRLEN len_test"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH idx_test 1 2 3", "LINDEX idx_test 0"],
        ["LPUSH idx_test 1 2 3", "LINDEX idx_test 2"],
        "NE"
    ))
    
    relations.append((
        ["LPUSH rem_test a b a c a", "LREM rem_test 2 a", "LLEN rem_test"],
        ["LPUSH rem_test a b a c a", "LREM rem_test 0 a", "LLEN rem_test"],
        "NE"
    ))
    
    relations.append((
        ["LPUSH rem_dir a b a", "LREM rem_dir 1 a", "LLEN rem_dir"],
        ["LPUSH rem_dir a b a", "LREM rem_dir -1 a", "LLEN rem_dir"],
        "EQ"
    ))
    
    relations.append((
        ["LPUSH lrev2 1 2 3", "LREV lrev2", "LRANGE lrev2 0 -1"],
        ["RPUSH lrev2 3 2 1", "LRANGE lrev2 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (- 0 5)"],
        ["EVAL -5"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (* -2 -3)"],
        ["EVAL 6"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (and (or 0 1) (not 0))"],
        ["EVAL 1"],
        "EQ"
    ))
    
    relations.append((
        ["EVAL (or (and 1 1) (not 0))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE rng TYPE integer RANGE 0 100", "SETV rng 0 TYPE integer RANGE 0 100"],
        ["DEFINE rng TYPE integer RANGE 0 100", "SETV rng 100 TYPE integer RANGE 0 100"],
        "EQ"
    ))
    
    relations.append((
        ["DEFINE rng TYPE integer RANGE 0 100", "SET rng 0", "SET rng 100"],
        ["DEFINE rng TYPE integer RANGE 0 100", "SET rng 50"],
        "NE"
    ))
    
    relations.append((
        ["DEFINE rng TYPE integer RANGE 0 100", "SETV rng 50 TYPE integer RANGE 0 100", "VALIDATE rng"],
        ["DEFINE rng TYPE integer RANGE 0 100", "SETV rng 150 TYPE integer RANGE 0 100"],
        "NE"
    ))
    
    relations.append((
        ["DEFINE dup TYPE integer RANGE 0 10", "DEFINE dup TYPE integer RANGE 0 20"],
        ["DEFINE dup TYPE integer RANGE 0 10"],
        "NE"
    ))
    

    

    relations.append((
        ["SET sl a", "STRLEN sl"],
        ["SET sl abc", "STRLEN sl"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH lr_test2 1 2 3", "LRANGE lr_test2 0 -1"],
        ["LPUSH lr_test2 1 2 3", "LREV lr_test2", "LRANGE lr_test2 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["SET d1 v1", "SET d2 v2", "DEL d1 d2"],
        ["SET d1 v1", "DEL d1"],
        "NE"
    ))
    

    relations.append((
        ["SET e1 a", "SET e2 b", "EXISTS e1 e2 e3"],
        ["SET e1 a", "EXISTS e1"],
        "NE"
    ))
    

    relations.append((
        ["SET a1 x", "APPEND a1 yz", "STRLEN a1"],
        ["SET a1 xyz", "STRLEN a1"],
        "EQ"
    ))
    

    relations.append((
        ["SET n1 10", "INCR n1", "GET n1"],
        ["SET n1 11"],
        "EQ"
    ))
    

    relations.append((
        ["SET n2 10", "DECR n2", "GET n2"],
        ["SET n2 9"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (and (and 1 1) (not 0))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET v1 5", "SET v2 3", "EVAL (+ $v1 $v2)"],
        ["EVAL 8"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (and (> 10 5) (< 3 5)) 100 200)"],
        ["EVAL 100"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lp_test a b c", "LPOP lp_test"],
        ["LPUSH lp_test2 c b a", "RPOP lp_test2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH ll_test 1 2 3 4", "LPOP ll_test", "LLEN ll_test"],
        ["LPUSH ll_test 1 2 3", "LLEN ll_test"],
        "NE"
    ))
    

    relations.append((
        ["SET m1 1", "SET m2 2", "MGET m1 m3"],
        ["SET m1 1", "MGET m1"],
        "NE"
    ))
    

    relations.append((
        ["SET sa1 hello", "APPEND sa1 world", "GET sa1"],
        ["SET sa1 helloworld"],
        "NE"
    ))
    

    relations.append((
        ["DEFINE vf TYPE integer RANGE 0 10", "SET vf 5", "VALIDATE vf"],
        ["DEFINE vf TYPE integer RANGE 0 10", "SET vf 15", "VALIDATE vf"],
        "NE"
    ))
    

    relations.append((
        ["DEFINE en_cs TYPE enum VALUES a,b,c", "SETV en_cs A TYPE enum VALUES a,b,c"],
        ["DEFINE en_cs TYPE enum VALUES A,B,C", "SETV en_cs A TYPE enum VALUES A,B,C"],
        "EQ"
    ))
    

    relations.append((
        ['DEFINE sm TYPE string PATTERN "^[0-9]+$"', "SET sm abc"],
        ["SET sm abc"],
        "NE"
    ))
    

    relations.append((
        ["EVAL (+ 1 2 3 4)"],
        ["EVAL (+ (+ 1 2) (+ 3 4))"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ -10 3)"],
        ["EVAL -3"],
        "EQ"
    ))
    

    relations.append((
        ["DEL"],
        ["DEL nonexistent"],
        "EQ"
    ))
    

    relations.append((
        ["SET c1 10", "INCR c1", "INCR c1", "DECRBY c1 2"],
        ["SET c1 12"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH ie_test a b c", "LINDEX ie_test 0"],
        ["LPUSH ie_test a b c", "LINDEX ie_test 5"],
        "NE"
    ))
    

    relations.append((
        ["SETV sv_test 10 TYPE integer RANGE 0 100", "GET sv_test"],
        ["SETV sv_test 20 TYPE integer RANGE 0 100", "GET sv_test"],
        "NE"
    ))
    

    relations.append((
        ["CALC cr (+ 100 200)", "GET cr"],
        ["SET cr 300", "GET cr"],
        "EQ"
    ))
    

    relations.append((
        ["SET mixed 123", "INCR mixed", "DECR mixed", "GET mixed"],
        ["SET mixed 123"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH rt a b c", "LREV rt", "LRANGE rt 0 -1"],
        ["LPUSH rt c b a", "LRANGE rt 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE bnd TYPE integer RANGE 5 5", "SETV bnd 5 TYPE integer RANGE 5 5"],
        ["DEFINE bnd TYPE integer RANGE 5 5", "SETV bnd 6 TYPE integer RANGE 5 5"],
        "NE"
    ))
    

    relations.append((
        ["EVAL $undef_var"],
        ["EVAL (+ $undef 1)"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (or (and 0 1) (and 1 0))"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH p1 1 2 3", "LPOP p1", "LPOP p1"],
        ["RPUSH p2 1 2 3", "RPOP p2", "RPOP p2"],
        "EQ"
    ))
    

    

    relations.append((
        ["EVAL (/ 10 2)"],
        ["EVAL (/ 12 2)"],
        "NE"
    ))
    

    relations.append((
        ["EVAL (/ -10 2)"],
        ["EVAL -5"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (% 10 3)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 0 100)"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ 1 2 3)"],
        ["EVAL (+ (+ 1 2) 3)"],
        "EQ"
    ))
    

    relations.append((
        ["SET m x1 5", "SET x2 10", "EVAL (+ $x1 $x2 $x1)"],
        ["EVAL 20"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (and (or 1 0) (not 0) (== 1 1))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrbd 1 2 3 4 5", "LRANGE lrbd 1 3"],
        ["LPUSH lrbd2 1 2 3 4 5", "LRANGE lrbd2 0 2"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH lset_t 1 2", "LSET lset_t 1 new"],
        ["LPUSH lset_t2 1 2", "LSET lset_t2 5 new"],
        "NE"
    ))
    

    relations.append((
        ["SET sa x", "APPEND sa yz", "STRLEN sa"],
        ["SET sa xyz", "STRLEN sa"],
        "EQ"
    ))
    

    relations.append((
        ["SET cov 1", "SET cov 2", "GET cov"],
        ["SET cov 2"],
        "EQ"
    ))
    

    relations.append((
        ["INCR newk1", "GET newk1"],
        ["SET newk2 1", "GET newk2"],
        "EQ"
    ))
    

    relations.append((
        ["SET ex1 a", "SET ex2 b", "EXISTS ex1 ex2 ex3"],
        ["SET ex1 a", "EXISTS ex1 ex2"],
        "NE"
    ))
    

    relations.append((
        ["DEFINE vt TYPE integer RANGE 0 100", "SETV vt 50 TYPE integer RANGE 0 100", "VALIDATE vt"],
        ["DEFINE vt TYPE integer RANGE 0 100", "SETV vt 150 TYPE integer RANGE 0 100", "VALIDATE vt"],
        "NE"
    ))
    

    relations.append((
        ["CALC calc2 (+ 5 10)", "GET calc2"],
        ["SET calc2 15", "GET calc2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ (* 2 3) (* 4 5))"],
        ["EVAL (* (+ 2 4) (+ 3 5))"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (or (and 1 0) 1)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (> 10 5) (if (< 3 4) 1 2) 3)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPOP empty_test"],
        ["RPOP empty_test"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrlen a b c", "LLEN lrlen"],
        ["LPUSH lrlen2 a b c", "LREV lrlen2", "LLEN lrlen2"],
        "EQ"
    ))
    

    relations.append((
        ["SET d1 v1", "SET d2 v2", "SET d3 v3", "DEL d1 d2 d3"],
        ["SET d1 v1", "DEL d1"],
        "NE"
    ))
    

    relations.append((
        ["SET gr_t hello", "GETRANGE gr_t 0 -1"],
        ["SET gr_t hello", "GET gr_t"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (< -5 -3)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET sn 123", "APPEND sn456 789", "GET sn"],
        ["SET sn456 789", "GET sn456"],
        "NE"
    ))
    

    relations.append((
        ["DEFINE rep TYPE integer RANGE 0 100", "DEFINE rep TYPE integer RANGE 0 200"],
        ["DEFINE rep TYPE integer RANGE 0 100"],
        "NE"
    ))




    relations.append((
        ["LPUSH lr1 a b c d", "LRANGE lr1 1 2"],
        ["LPUSH lr2 a b c d", "LRANGE lr2 0 1"],
        "NE"
    ))

    relations.append((
        ["LPUSH lr3 1 2 3", "LRANGE lr3 0 0"],
        ["LPUSH lr4 1 2 3", "LINDEX lr4 0"],
        "EQ"
    ))

    relations.append((
        ["LPUSH lr5 a b c", "LRANGE lr5 0 10"],
        ["LPUSH lr6 a b c", "LRANGE lr6 0 -1"],
        "EQ"
    ))

    relations.append((
        ["LPUSH lr7 1 2 3", "LRANGE lr7 -1 -1"],
        ["LPUSH lr8 1 2 3", "LINDEX lr8 -1"],
        "EQ"
    ))

    relations.append((
        ["LPUSH lr9 1 2 3", "LRANGE lr9 5 10"],
        ["LPUSH lr10 1 2 3", "LRANGE lr10 10 20"],
        "EQ"
    ))


    relations.append((
        ["LPUSH lr11 a b a c a", "LREM lr11 0 a", "LLEN lr11"],
        ["LPUSH lr12 a b a c a", "LLEN lr12"],
        "NE"
    ))

    relations.append((
        ["LPUSH lr13 a b c", "LREM lr13 1 x", "LLEN lr13"],
        ["LPUSH lr14 a b c", "LLEN lr14"],
        "EQ"
    ))

    relations.append((
        ["LPUSH lr15 a b a c", "LREM lr15 -1 a", "LLEN lr15"],
        ["LPUSH lr16 a b a c", "LREM lr16 1 a", "LLEN lr16"],
        "NE"
    ))

    relations.append((
        ["LPUSH lr17 1 2 3", "LREM lr17 100 a", "LLEN lr17"],
        ["LPUSH lr18 1 2 3", "LLEN lr18"],
        "EQ"
    ))

    relations.append((
        ["LPUSH lr19 a b c", "LREM lr19 0 x", "LLEN lr19"],
        ["LPUSH lr20 a b c", "LLEN lr20"],
        "EQ"
    ))


    relations.append((
        ["LPUSH ls1 1 2 3", "LSET ls1 0 new", "LINDEX ls1 0"],
        ["LPUSH ls2 1 2 3", "LSET ls2 2 new", "LINDEX ls2 2"],
        "NE"
    ))

    relations.append((
        ["LPUSH ls3 1 2 3", "LSET ls3 5 x"],
        ["LPUSH ls4 1 2 3", "LSET ls4 -5 x"],
        "EQ"
    ))

    relations.append((
        ["LPUSH ls5 1 2 3", "LSET ls5 -1 last", "LINDEX ls5 -1"],
        ["LPUSH ls6 1 2 3", "LSET ls6 2 last", "LINDEX ls6 2"],
        "EQ"
    ))


    relations.append((
        ["DEFINE v1 TYPE integer RANGE 0 100", "SETV v1 0 TYPE integer RANGE 0 100", "VALIDATE v1"],
        ["DEFINE v2 TYPE integer RANGE 0 100", "SETV v2 100 TYPE integer RANGE 0 100", "VALIDATE v2"],
        "EQ"
    ))

    relations.append((
        ["DEFINE v3 TYPE integer RANGE -50 50", "SETV v3 -50 TYPE integer RANGE -50 50", "VALIDATE v3"],
        ["DEFINE v4 TYPE integer RANGE -50 50", "SETV v4 50 TYPE integer RANGE -50 50", "VALIDATE v4"],
        "EQ"
    ))

    relations.append((
        ["DEFINE v5 TYPE integer RANGE 0 100", "SETV v5 50 TYPE integer RANGE 0 100", "VALIDATE v5"],
        ["DEFINE v6 TYPE integer RANGE 0 100", "SETV v6 150 TYPE integer RANGE 0 100", "VALIDATE v6"],
        "NE"
    ))

    relations.append((
        ['DEFINE v7 TYPE string PATTERN "^[a-z]+$"', 'SETV v7 abc TYPE string PATTERN "^[a-z]+$"', "VALIDATE v7"],
        ['DEFINE v8 TYPE string PATTERN "^[0-9]+$"', 'SETV v8 123 TYPE string PATTERN "^[0-9]+$"', "VALIDATE v8"],
        "EQ"
    ))

    relations.append((
        ['DEFINE v9 TYPE string PATTERN "^[a-z]+$"', 'SETV v9 123 TYPE string PATTERN "^[a-z]+$"', "VALIDATE v9"],
        ['DEFINE v10 TYPE string PATTERN "^[a-z]+$"', 'SETV v10 ABC TYPE string PATTERN "^[a-z]+$"', "VALIDATE v10"],
        "NE"
    ))


    relations.append((
        ["EVAL (- 10 5 3)"],
        ["EVAL 2"],
        "EQ"
    ))

    relations.append((
        ["EVAL (* 2 3 4)"],
        ["EVAL 24"],
        "EQ"
    ))

    relations.append((
        ["SET x 5", "SET y 3", "SET z 2", "EVAL (+ $x $y $z)"],
        ["EVAL 10"],
        "EQ"
    ))

    relations.append((
        ["EVAL (< 0 1)"],
        ["EVAL 1"],
        "EQ"
    ))

    relations.append((
        ["EVAL (> 0 1)"],
        ["EVAL 0"],
        "EQ"
    ))


    relations.append((
        ["LPUSH rv1 a b c", "LREV rv1", "LRANGE rv1 0 0"],
        ["LPUSH rv2 c b a", "LRANGE rv2 0 0"],
        "EQ"
    ))

    relations.append((
        ["LPUSH rv3 1 2 3", "LREV rv3", "LINDEX rv3 0"],
        ["LPUSH rv4 1 2 3", "LINDEX rv4 2"],
        "EQ"
    ))

    relations.append((
        ["LPUSH rv5 1 2 3", "LREV rv5", "LREV rv5"],
        ["LPUSH rv6 1 2 3", "LRANGE rv6 0 -1"],
        "EQ"
    ))

    relations.append((
        ["LPUSH rv7 x", "LREV rv7"],
        ["LPUSH rv8 x"],
        "EQ"
    ))

    relations.append((
        ["LPUSH rv9 a b c d", "LREV rv9", "LLEN rv9"],
        ["LPUSH rv10 a b c d", "LLEN rv10"],
        "EQ"
    ))


    relations.append((
        ["SET st1 hello", "APPEND st1 world", "GET st1"],
        ["SET st1 helloworld"],
        "EQ"
    ))

    relations.append((
        ["SET st2", "STRLEN st2"],
        ["SET st3 empty_val", "STRLEN st3"],
        "NE"
    ))

    relations.append((
        ["SET st4 a", "APPEND st4", "GET st4"],
        ["SET st5 a"],
        "NE"
    ))

    relations.append((
        ["SET st6 test", "DEL st6", "EXISTS st6"],
        ["SET st7", "EXISTS st7"],
        "EQ"
    ))

    relations.append((
        ["SET st8 value", "GET st8", "GET st8"],
        ["SET st9 value", "GET st9"],
        "EQ"
    ))


    relations.append((
        ["SET n1 10", "INCR n1", "INCR n1", "DECR n1", "GET n1"],
        ["SET n2 11"],
        "EQ"
    ))

    relations.append((
        ["SET n3 5", "INCRBY n3 10", "DECRBY n3 3", "GET n3"],
        ["SET n4 12"],
        "EQ"
    ))

    relations.append((
        ["LPUSH lc1 1 2", "LPOP lc1", "LPUSH lc1 3", "LRANGE lc1 0 -1"],
        ["LPUSH lc2 2", "LPUSH lc2 3", "LRANGE lc2 0 -1"],
        "NE"
    ))

    relations.append((
        ["DEFINE c1 TYPE integer RANGE 0 100", "SETV c1 50 TYPE integer RANGE 0 100", "VALIDATE c1", "VALIDATE c1"],
        ["DEFINE c2 TYPE integer RANGE 0 100", "SETV c2 50 TYPE integer RANGE 0 100", "VALIDATE c2"],
        "EQ"
    ))

    relations.append((
        ["CALC c3 (+ 1 2)", "CALC c3 (+ $c3 3)", "GET c3"],
        ["SET c4 6", "GET c4"],
        "EQ"
    ))


    relations.append((
        ["LPUSH ml1 a b c", "LPUSH ml1", "LLEN ml1"],
        ["LPUSH ml2 a b c", "LLEN ml2"],
        "NE"
    ))

    relations.append((
        ["SET m1 1", "SET m2 2", "SET m3 3", "DEL m1 m2", "EXISTS m1 m2 m3"],
        ["SET m4 3", "EXISTS m4"],
        "NE"
    ))

    relations.append((
        ["EVAL (== 0 0)"],
        ["EVAL 1"],
        "EQ"
    ))

    relations.append((
        ["EVAL (!= 5 5)"],
        ["EVAL 0"],
        "EQ"
    ))

    relations.append((
        ["SET v1 1", "SET v2 2", "EVAL (+ $v1 $v2)"],
        ["SET v3 3", "GET v3"],
        "NE"
    ))


    relations.append((
        ["LPUSH e1 1", "LINDEX e1 100"],
        ["LPUSH e2 1", "LINDEX e2 -100"],
        "EQ"
    ))

    relations.append((
        ["SET e3 1", "INCR e3", "INCRBY e3"],
        ["SET e4 1", "INCRBY e4"],
        "NE"
    ))

    relations.append((
        ["EVAL (/ 0 0)"],
        ["EVAL (% 0 0)"],
        "EQ"
    ))

    relations.append((
        ["GET e5"],
        ["LINDEX e6 0"],
        "EQ"
    ))

    relations.append((
        ["SET e7 val", "DEL e7", "GET e7"],
        ["GET e8"],
        "EQ"
    ))


    relations.append((
        ["EVAL (+ (- 10 5) (* 2 3))"],
        ["EVAL 11"],
        "EQ"
    ))

    relations.append((
        ["EVAL (* (+ 1 2) (- 10 5))"],
        ["EVAL 15"],
        "EQ"
    ))

    relations.append((
        ["EVAL (if (and 1 (not 0)) 100 200)"],
        ["EVAL 100"],
        "EQ"
    ))

    relations.append((
        ["EVAL (if (or 0 (not 1)) a b)"],
        ["EVAL b"],
        "EQ"
    ))

    relations.append((
        ["SET x 10", "EVAL (+ $x $x $x $x $x)"],
        ["EVAL 50"],
        "EQ"
    ))




    relations.append((
        ["LPUSH lp_order 1 2 3", "LRANGE lp_order 0 -1"],
        ["RPUSH rp_order 3 2 1", "LRANGE rp_order 0 -1"],
        "EQ"
    ))


    relations.append((
        ["LPUSH rev_eq 1 2 3", "LREV rev_eq", "LRANGE rev_eq 0 -1"],
        ["RPUSH rp_eq 1 2 3", "LRANGE rp_eq 0 -1"],
        "EQ"
    ))


    relations.append((
        ["LPUSH pop_cnt 1 2 3 4 5", "LPOP pop_cnt", "LPOP pop_cnt", "LLEN pop_cnt"],
        ["SET ref 3"],
        "EQ"
    ))


    relations.append((
        ["LPUSH rem_zero a b c", "LREM rem_zero 0 x", "LLEN rem_zero"],
        ["LPUSH rem_ref b c", "LLEN rem_ref"],
        "NE"
    ))


    relations.append((
        ["SET app_cum x", "APPEND app_cum a", "APPEND app_cum bc", "APPEND app_cum d", "GET app_cum"],
        ["SET ref xabcd"],
        "EQ"
    ))


    relations.append((
        ["SET strlen_eq abc", "APPEND strlen_eq def", "STRLEN strlen_eq"],
        ["SET ref 6"],
        "EQ"
    ))


    relations.append((
        ["SET incr_decr 0", "INCR incr_decr", "INCR incr_decr", "INCR incr_decr", "DECR incr_decr", "GET incr_decr"],
        ["SET ref 2"],
        "EQ"
    ))


    relations.append((
        ["SET num_dir 10", "INCRBY num_dir 5", "DECRBY num_dir 3", "GET num_dir"],
        ["SET ref 12"],
        "EQ"
    ))


    relations.append((
        ["SET del_exist val", "DEL del_exist", "EXISTS del_exist"],
        ["EXISTS del_no_exist"],
        "NE"
    ))


    relations.append((
        ["SET ex1 a", "SET ex2 b", "SET ex3 c", "EXISTS ex1 ex2 ex3"],
        ["SET ref 3"],
        "EQ"
    ))


    relations.append((
        ["DEFINE rng_min TYPE integer RANGE 0 10", "SETV rng_min 0 TYPE integer RANGE 0 10", "VALIDATE rng_min"],
        ["DEFINE rng_max TYPE integer RANGE 0 10", "SETV rng_max 10 TYPE integer RANGE 0 10", "VALIDATE rng_max"],
        "EQ"
    ))


    relations.append((
        ["DEFINE rng_under TYPE integer RANGE 0 10", "SETV rng_under -1 TYPE integer RANGE 0 10", "VALIDATE rng_under"],
        ["DEFINE rng_over TYPE integer RANGE 0 10", "SETV rng_over 11 TYPE integer RANGE 0 10", "VALIDATE rng_over"],
        "EQ"
    ))


    relations.append((
        ['DEFINE pat_match TYPE string PATTERN "^[0-9]+$"', 'SETV pat_match 12345 TYPE string PATTERN "^[0-9]+$"', "VALIDATE pat_match"],
        ['DEFINE pat_nomatch TYPE string PATTERN "^[0-9]+$"', 'SETV pat_nomatch abc TYPE string PATTERN "^[0-9]+$"', "VALIDATE pat_nomatch"],
        "NE"
    ))


    relations.append((
        ["DEFINE enum_strict TYPE enum VALUES red,green,blue", "SETV enum_strict red TYPE enum VALUES red,green,blue", "VALIDATE enum_strict"],
        ["DEFINE enum_nomatch TYPE enum VALUES red,green,blue", "SETV enum_nomatch yellow TYPE enum VALUES red,green,blue", "VALIDATE enum_nomatch"],
        "NE"
    ))


    relations.append((
        ["CALC chain1 (+ 1 2)", "CALC chain2 (+ $chain1 3)", "CALC chain3 (+ $chain2 4)", "CALC chain4 (+ $chain3 5)", "GET chain4"],
        ["CALC chain_ref (+ 1 2 3 4 5)", "GET chain_ref"],
        "EQ"
    ))


    relations.append((
        ["SET calc_x 3", "SET calc_y 4", "CALC calc_pythag (+ (* $calc_x $calc_x) (* $calc_y $calc_y))", "GET calc_pythag"],
        ["CALC calc_ref (+ (* 3 3) (* 4 4))", "GET calc_ref"],
        "EQ"
    ))


    relations.append((
        ["EVAL (+ 1 2 3 4 5)"],
        ["EVAL (+ (+ 1 2 3) 4 5)"],
        "EQ"
    ))


    relations.append((
        ["EVAL (* (+ 1 2) (+ 3 4))"],
        ["EVAL (+ (* 1 3) (* 1 4) (* 2 3) (* 2 4))"],
        "EQ"
    ))


    relations.append((
        ["EVAL (not (and 1 0))"],
        ["EVAL (or (not 1) (not 0))"],
        "EQ"
    ))


    relations.append((
        ["EVAL (if 0 (/ 1 0) 42)"],
        ["SET ref 42"],
        "EQ"
    ))


    relations.append((
        ["LPUSH idx_bound 1 2 3", "LRANGE idx_bound 0 100"],
        ["LPUSH idx_ref 1 2 3", "LRANGE idx_ref 0 -1"],
        "EQ"
    ))


    relations.append((
        ["LPUSH neg_idx 1 2 3 4 5", "LRANGE neg_idx 2 4"],
        ["LPUSH neg_idx2 1 2 3 4 5", "LRANGE neg_idx2 -3 -1"],
        "EQ"
    ))


    relations.append((
        ["LPUSH lin_neg 1 2 3 4 5", "LINDEX lin_neg -1"],
        ["SET ref 5"],
        "EQ"
    ))


    relations.append((
        ["LPUSH lset_pos a b c d", "LSET lset_pos 1 X", "LINDEX lset_pos 0"],
        ["SET ref a"],
        "EQ"
    ))


    relations.append((
        ["LPUSH lset_new a b c d", "LSET lset_new 2 NEW", "LINDEX lset_new 2"],
        ["SET ref NEW"],
        "EQ"
    ))


    relations.append((
        ["LPUSH rev_len 1 2 3 4 5 6", "LREV rev_len", "LLEN rev_len"],
        ["SET ref 6"],
        "EQ"
    ))


    relations.append((
        ["MSET ms_a1 v1 ms_a2 v2 ms_a3 v3", "MGET ms_a1 ms_a2 ms_a3"],
        ["SET ms_ref1 v1", "SET ms_ref2 v2", "SET ms_ref3 v3", "MGET ms_a1 ms_a2 ms_a3"],
        "NE"
    ))


    relations.append((
        ["SET num_str 123", "INCR num_str", "GET num_str"],
        ["SET ref 124"],
        "EQ"
    ))


    relations.append((
        ["LPUSH lcnt a b a c a", "LREM lcnt 0 a", "LLEN lcnt"],
        ["SET ref 2"],
        "EQ"
    ))


    relations.append((
        ["SET cover a", "SET cover b", "SET cover c", "GET cover"],
        ["SET ref c"],
        "EQ"
    ))


    relations.append((
        ["LPUSH empty 1", "LPOP empty", "LLEN empty"],
        ["SET ref 0"],
        "EQ"
    ))


    relations.append((
        ["LPUSH noargs"],
        ["LPUSH noargs2 1", "LPOP noargs2"],
        "EQ"
    ))


    relations.append((
        ["SET grange abcdef", "GETRANGE grange 0 0"],
        ["SET ref a"],
        "EQ"
    ))


    relations.append((
        ["SET grange2 abcdef", "GETRANGE grange2 -2 -1"],
        ["SET ref ef"],
        "EQ"
    ))


    relations.append((
        ["EVAL (+ $undef_var 1)"],
        ["EVAL (+ $another_undef 1)"],
        "EQ"
    ))


    relations.append((
        ["EVAL (/ 7 2)"],
        ["EVAL (+ (/ 6 2) (/ 1 2))"],
        "EQ"
    ))


    relations.append((
        ["EVAL (+ (* (/ 10 3) 3) (% 10 3))"],
        ["SET ref 10"],
        "EQ"
    ))


    relations.append((
        ["LPUSH rem_pos_neg a b a c a", "LREM rem_pos_neg 2 a", "LLEN rem_pos_neg"],
        ["SET ref 3"],
        "EQ"
    ))


    relations.append((
        ["SET overflow 0", "INCRBY overflow 999999", "DECRBY overflow 999999", "GET overflow"],
        ["SET ref 0"],
        "EQ"
    ))


    relations.append((
        ["EVAL (if (if 1 0 1) 100 200)"],
        ["SET ref 200"],
        "EQ"
    ))


    relations.append((
        ["LPUSH type_a 1 2 3", "GET type_a"],
        ["LPUSH type_b 1 2 3", "GET type_b"],
        "EQ"
    ))


    relations.append((
        ["SET type_str val", "LLEN type_str"],
        ["SET type_str2 val", "LLEN type_str2"],
        "EQ"
    ))


    relations.append((
        ["SET del_key key", "DEL del_key", "EXISTS del_key"],
        ["EXISTS no_key_exists"],
        "NE"
    ))


    relations.append((
        ["SET deci 0", "DECR deci", "DECR deci", "DECR deci", "INCR deci", "GET deci"],
        ["SET ref -2"],
        "EQ"
    ))


    relations.append((
        ["LPUSH rev_single x", "LREV rev_single", "LINDEX rev_single 0"],
        ["SET ref x"],
        "EQ"
    ))


    relations.append((
        ["SET mix_incr 1", "INCR mix_incr", "APPEND mix_incr val", "GET mix_incr"],
        ["SET ref 2val"],
        "EQ"
    ))


    relations.append((
        ["LPUSH first_last 1 2 3 4 5", "LRANGE first_last 0 0"],
        ["LPUSH first_last2 1 2 3 4 5", "LINDEX first_last2 0"],
        "EQ"
    ))


    relations.append((
        ["LPUSH double 1 2 3", "LREV double", "LREV double", "LRANGE double 0 -1"],
        ["LPUSH single 1 2 3", "LRANGE single 0 -1"],
        "EQ"
    ))


    relations.append((
        ["CALC calcm1 (+ 10 20 30)", "GET calcm1"],
        ["SET ref 60"],
        "EQ"
    ))


    relations.append((
        ["SET cx 2", "SET cy 3", "SET cz 4", "EVAL (+ (* $cx $cx) (* $cy $cy) (* $cz $cz))"],
        ["CALC ccalc (+ (* 2 2) (* 3 3) (* 4 4))", "GET ccalc"],
        "EQ"
    ))
    

    

    for i in range(5):
        relations.append((
            [f"SET n {i}", "INCR n", "DECR n", "GET n"],
            [f"SET n {i}"],
            "EQ"
        ))
    

    relations.append((
        ["LPUSH lst 1 2 3", "LRANGE lst 0 -1"],
        ["RPUSH lst 3 2 1", "LRANGE lst 0 -1"],
        "EQ"
    ))
    

    for _ in range(3):
        relations.append((
            ["LPUSH test a b c", "LPOP test", "LPOP test", "LLEN test"],
            ["SET test_len 1"],
            "EQ"
        ))
    

    relations.append((
        ["LPUSH outer 1 2", "LPUSH inner 3 4", "LPUSH outer 5 6", "LLEN outer"],
        ["SET outer_len 4"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH arr 1 2 3", "LSET arr 0 9", "LSET arr 2 9", "LREV arr", "LINDEX arr 1"],
        ["SET idx 2"],
        "EQ"
    ))
    

    relations.append((
        ["MSET m1 v1 m2 v2 m3 v3", "MSET m1 new1", "GET m1"],
        ["SET m1 new1", "GET m1"],
        "EQ"
    ))
    

    relations.append((
        ["SET a 1", "SET b 2", "MGET a b c d"],
        ["SET a 1", "SET b 2", "MGET a b"],
        "NE"
    ))
    

    relations.append((
        ["SET s abcde", "GETRANGE s 0 2"],
        ["SET s abcde", "GETRANGE s 0 -3"],
        "EQ"
    ))
    relations.append((
        ["SET s abcde", "GETRANGE s 2 4"],
        ["SET s abcde", "GETRANGE s -3 -1"],
        "EQ"
    ))
    

    for length in [3, 5, 10]:
        s = "a" * length
        relations.append((
            ["SET s ''", "APPEND s a", "APPEND s " + "a" * (length-1), "STRLEN s"],
            [f"SET s {s}", "STRLEN s"],
            "EQ"
        ))
    

    relations.append((
        ["LPUSH remall a b a c a", "LREM remall 0 a", "LLEN remall"],
        ["SET remall_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH neg 1 2 3 4 5", "LRANGE neg -2 -1"],
        ["SET neg_val 2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH full 1 2 3 4 5", "LINDEX full -1"],
        ["SET full_val 5"],
        "EQ"
    ))
    

    for i in range(3):
        relations.append((
            [f"CALC r (+ 1 {i})", "CALC r (+ $r 2)", "GET r"],
            [f"SET r {3+i}"],
            "EQ"
        ))
    

    relations.append((
        ["SET x 5", "SET y 3", "EVAL (+ (* $x 2) $y)"],
        ["EVAL 13"],
        "EQ"
    ))
    

    relations.append((
        ["SET a 10", "SET b 20", "EVAL (if (< $a $b) $a $b)"],
        ["EVAL 10"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (and (or 1 0) (not 0))"],
        ["EVAL 1"],
        "EQ"
    ))
    relations.append((
        ["EVAL (or (and 1 0) (not 1))"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ (* (/ 10 3) 3) (% 10 3))"],
        ["EVAL 10"],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE v TYPE integer RANGE 0 100", "SETV v 50 TYPE integer RANGE 0 100", "GET v"],
        ["SET v 50", "GET v"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lst 1 2 3", "GET lst"],
        ["SET lst 1 2 3", "GET lst"],
        "NE"
    ))
    

    relations.append((
        ["SET d1 a", "SET d2 b", "DEL d1", "DEL d2", "EXISTS d1"],
        ["SET d1 a", "EXISTS d1"],
        "NE"
    ))
    

    for delta in [5, 10, 15]:
        relations.append((
            [f"SET n 0", f"INCRBY n {delta}", f"DECRBY n {delta}", "GET n"],
            ["SET n 0"],
            "EQ"
        ))
    

    for start, end, expected in [(0, 0, 1), (0, 1, 2), (1, 2, 2)]:
        relations.append((
            [f"LPUSH range 1 2 3", f"LRANGE range {start} {end}"],
            [f"SET range_len {expected}"],
            "EQ"
        ))
    

    relations.append((
        ["SET num 100", "APPEND num suffix", "STRLEN num"],
        ["SET num 100", "STRLEN num"],
        "NE"
    ))
    

    relations.append((
        ["EVAL (+ $no_such_var 1)"],
        ["EVAL (+ $another_no_such 2)"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 1 0)"],
        ["EVAL (/ 100 0)"],
        "EQ"
    ))
    

    relations.append((
        ["SET str_val hello", "LLEN str_val"],
        ["SET str_val2 world", "LLEN str_val2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lset 1 2 3", "LSET lset 0 9", "LSET lset -1 9", "LRANGE lset 0 -1"],
        ["SET lset_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET s hello", "STRLEN s", "APPEND s world", "STRLEN s"],
        ["SET s helloworld", "STRLEN s"],
        "EQ"
    ))
    

    relations.append((
        ["SET e1 v", "EXISTS e1", "DEL e1", "EXISTS e1"],
        ["SET e1 v", "EXISTS noexist"],
        "NE"
    ))
    

    relations.append((
        ["SET v1 10", "SET v2 20", "SET v3 30", "EVAL (+ $v1 $v2 $v3)"],
        ["EVAL 60"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (if 0 1 0) (if 1 100 200) (if 0 300 400))"],
        ["EVAL 400"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (< (+ 1 2) (* 2 2))"],
        ["EVAL 1"],
        "EQ"
    ))
    relations.append((
        ["EVAL (> (+ 1 2) (* 2 2))"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rev 1 2 3", "LREV rev", "LREV rev", "LREV rev"],
        ["LPUSH rev2 1 2 3", "LREV rev2"],
        "EQ"
    ))
    

    relations.append((
        ["SET concat ''", "APPEND concat a", "APPEND concat b", "APPEND concat c", "GET concat"],
        ["SET concat abc"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH order 1", "LPUSH order 2", "LPUSH order 3", "LLEN order"],
        ["SET order_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET a 5", "SET b 10", "EVAL (if (< $a $b) (+ $a $b) (- $a $b))"],
        ["EVAL 15"],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE v TYPE integer RANGE 0 100", "SETV v 50 TYPE integer RANGE 0 100", "VALIDATE v", "GET v"],
        ["SET v 50"],
        "NE"
    ))
    

    relations.append((
        ["LPOP emptypop"],
        ["RPOP emptypop2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH llen 1 2 3", "LLEN llen", "LPUSH llen 4", "LLEN llen"],
        ["LPUSH llen2 1 2 3 4", "LLEN llen2"],
        "EQ"
    ))
    

    relations.append((
        ["MSET m1 a m2 b m3 c", "MGET m1 m2 m3"],
        ["SET m1 a", "SET m2 b", "SET m3 c", "MGET m1 m2 m3"],
        "EQ"
    ))
    

    relations.append((
        ["SETV b1 0 TYPE integer RANGE 0 100", "GET b1"],
        ["SET b1 0", "GET b1"],
        "EQ"
    ))
    relations.append((
        ["SETV b2 100 TYPE integer RANGE 0 100", "GET b2"],
        ["SET b2 100", "GET b2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ 1)"],
        ["EVAL (* 2)"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH single x", "LLEN single"],
        ["SET single_len 1"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ (- 100 50) (* 3 4) (/ 20 5))"],
        ["EVAL 66"],
        "EQ"
    ))
    

    relations.append((
        ["SET rebuild value", "DEL rebuild", "SET rebuild newvalue", "GET rebuild"],
        ["SET rebuild newvalue"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH negidx 1 2 3", "LINDEX negidx -2"],
        ["SET negidx_val 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET eq1 hello", "SET eq2 hello", "EVAL (== $eq1 $eq2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET neq1 hello", "SET neq2 world", "EVAL (!= $neq1 $neq2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH llenr 1 2 3 4 5", "LRANGE llenr 0 0"],
        ["SET llenr_first 1"],
        "EQ"
    ))
    

    for expr in ["(+ 1 2)", "(- 10 5)", "(* 3 4)", "(/ 20 4)", "(% 10 3)"]:
        relations.append((
            [f"CALC res {expr}", "GET res"],
            [f"EVAL {expr}"],
            "EQ"
        ))
    

    relations.append((
        ["LPUSH setout 1 2 3", "LSET setout 10 x"],
        ["LPUSH setout2 1 2 3", "LSET setout2 -10 y"],
        "EQ"
    ))
    

    relations.append((
        ["SET nonnum hello", "INCR nonnum"],
        ["SET nonnum hello", "DECR nonnum"],
        "EQ"
    ))
    

    for i in range(3):
        relations.append((
            [f"SET a {i}", f"SET b {i+1}", f"EVAL (+ $a $b)"],
            [f"EVAL {2*i+1}"],
            "EQ"
        ))
    

    relations.append((
        ["LPUSH revlen 1 2 3 4 5", "LREV revlen", "LLEN revlen"],
        ["SET revlen_len 5"],
        "EQ"
    ))
    

    relations.append((
        ["SET empty ''", "GETRANGE empty 0 -1"],
        ["GET empty"],
        "EQ"
    ))
    

    relations.append((
        ["SET mix 10", "INCR mix", "SET mix 20", "INCR mix"],
        ["SET mix 21"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rembound a b c", "LREM rembound 100 a"],
        ["LPUSH rembound2 a b c", "LREM rembound2 1 a"],
        "NE"
    ))
    

    relations.append((
        ["SET strnum 123", "INCR strnum"],
        ["SET strnum2 123", "INCR strnum2"],
        "EQ"
    ))
    

    relations.append((
        ["SET f1 5", "SET f2 10", "EVAL (+ (* $f1 2) (* $f2 2))"],
        ["EVAL 30"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lget 1 2 3", "GET lget"],
        ["SET lget 1 2 3", "GET lget"],
        "EQ"
    ))
    

    relations.append((
        ["SET mix 10", "INCR mix", "SET mix 20", "INCR mix"],
        ["SET mix 21"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rembound a b c", "LREM rembound 100 a"],
        ["LPUSH rembound2 a b c", "LREM rembound2 1 a"],
        "NE"
    ))
    

    relations.append((
        ["SET strnum 123", "INCR strnum"],
        ["SET strnum2 123", "INCR strnum2"],
        "EQ"
    ))
    

    relations.append((
        ["SET f1 5", "SET f2 10", "EVAL (+ (* $f1 2) (* $f2 2))"],
        ["EVAL 30"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lget 1 2 3", "GET lget"],
        ["SET lget 1 2 3", "GET lget"],
        "EQ"
    ))
    

    

    relations.append((
        ["LPUSH lst_op 1", "LLEN lst_op"],
        ["SET str_op 1", "STRLEN str_op"],
        "EQ"
    ))
    

    relations.append((
        ["SET deln a", "DEL deln", "EXISTS deln"],
        ["EXISTS deln2"],
        "EQ"
    ))
    

    relations.append((
        ["SET s1 abc", "APPEND s1 d", "STRLEN s1"],
        ["SET s2 abcdef", "STRLEN s2"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH lp_first 1 2 3", "LINDEX lp_first 0"],
        ["RPUSH rp_first 1 2 3", "LINDEX rp_first 0"],
        "NE"
    ))
    

    relations.append((
        ["SET cmp1 5", "SET cmp2 10", "EVAL (< $cmp1 $cmp2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsetm 1 2 3", "LSET lsetm 1 9", "LINDEX lsetm 1"],
        ["SET lsetm_val 9"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lenop 1 2", "LPUSH lenop 3", "LLEN lenop"],
        ["SET lenop_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["MSET ms1 a ms2 b ms3 c", "GET ms2"],
        ["SET ms2 b"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 7 2)"],
        ["EVAL 3"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (% 7 2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET incrby 0", "INCRBY incrby 10"],
        ["SET incrby 10"],
        "EQ"
    ))
    

    relations.append((
        ["SET decrby 10", "DECRBY decrby 3"],
        ["SET decrby 7"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH popdif 1 2 3", "LPOP popdif"],
        ["LPUSH popdif2 1 2 3", "RPOP popdif2"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH llenemp 1", "LPOP llenemp", "LLEN llenemp"],
        ["LLEN llennone"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rangeb 1 2 3", "LRANGE rangeb 0 100"],
        ["LPUSH rangeb2 1 2 3", "LRANGE rangeb2 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH idxout 1 2 3", "LINDEX idxout 100"],
        ["LPUSH idxout2 1 2 3", "LINDEX idxout2 -100"],
        "EQ"
    ))
    

    relations.append((
        ["SET seq a", "SET seq b", "GET seq"],
        ["SET seq b"],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE d1 TYPE integer RANGE 0 100", "SET d1 50"],
        ["SET d1 50"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (and 1 (or 0 1))"],
        ["EVAL 1"],
        "EQ"
    ))
    relations.append((
        ["EVAL (or 0 (and 1 0))"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (< 1 2 3)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (not 0) (if 1 10 20) 30)"],
        ["EVAL 10"],
        "EQ"
    ))
    

    relations.append((
        ["SET c1 5", "CALC cres (+ $c1 10)", "GET cres"],
        ["CALC cres2 (+ 5 10)", "GET cres2"],
        "EQ"
    ))
    

    relations.append((
        ["SET m1 v1", "MGET m1 m2 m3"],
        ["SET m1 v1", "MGET m1 m2"],
        "NE"
    ))
    

    relations.append((
        ["SET sub hello", "GETRANGE sub 1 3"],
        ["SET sub_val el"],
        "EQ"
    ))
    

    relations.append((
        ["SET empty_s ''", "STRLEN empty_s"],
        ["SET empty_s_len 0"],
        "EQ"
    ))
    

    relations.append((
        ["SET exdel x", "DEL exdel", "EXISTS exdel"],
        ["EXISTS nox"],
        "EQ"
    ))
    

    for count in [0, 1, 2, -1, -2]:
        relations.append((
            [f"LPUSH remc a b a c a", f"LREM remc {count} a", "LLEN remc"],
            [f"SET remc_len {2 if count == 0 else (2 if count > 0 else 3 if count == -2 else 1)}"],
            "EQ"
        ))
    

    relations.append((
        ["SET mi 0", "INCR mi", "INCR mi", "INCR mi", "GET mi"],
        ["SET mi3 3"],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE sv TYPE integer RANGE 0 100", "SETV sv 50 TYPE integer RANGE 0 100", "GET sv"],
        ["SET sv50 50"],
        "NE"
    ))
    

    relations.append((
        ["SET cmp_s1 abc", "SET cmp_s2 abc", "EVAL (== $cmp_s1 $cmp_s2)"],
        ["EVAL 1"],
        "EQ"
    ))
    relations.append((
        ["SET cmp_s3 abc", "SET cmp_s4 def", "EVAL (== $cmp_s3 $cmp_s4)"],
        ["EVAL 0"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rev_even 1 2 3 4", "LREV rev_even", "LRANGE rev_even 0 -1"],
        ["SET rev_even_val 1 2 3 4"],
        "EQ"
    ))
    relations.append((
        ["LPUSH rev_odd 1 2 3", "LREV rev_odd", "LRANGE rev_odd 0 -1"],
        ["SET rev_odd_val 1 2 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET nonnum_incr hello", "INCR nonnum_incr"],
        ["SET nonnum_decr hello", "DECR nonnum_decr"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 0 0)"],
        ["EVAL (% 0 0)"],
        "EQ"
    ))
    

    relations.append((
        ["SET vc 50", "EVAL (> $vc 40)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lkey a b c", "GET lkey"],
        ["SET lkey2 a b c", "GET lkey2"],
        "EQ"
    ))
    

    relations.append((
        ["DEFINE vald TYPE integer RANGE 0 100", "SETV vald 50 TYPE integer RANGE 0 100", "VALIDATE vald"],
        ["DEFINE vald2 TYPE integer RANGE 0 100", "SETV vald2 50 TYPE integer RANGE 0 100"],
        "NE"
    ))
    

    relations.append((
        ["SET str a", "LPUSH lst b", "EXISTS str"],
        ["SET str2 c", "EXISTS str2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH idxlp 5 4 3 2 1", "LINDEX idxlp 2"],
        ["SET idxlp_val 3"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (* (+ 1 2) (- 10 5) (/ 6 2))"],
        ["EVAL 45"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH setfe a b c", "LSET setfe 0 x", "LSET setfe -1 y", "LRANGE setfe 0 -1"],
        ["SET setfe_res x b y"],
        "EQ"
    ))
    

    relations.append((
        ["SET cov a", "SET cov b", "SET cov c", "GET cov"],
        ["SET cov3 c"],
        "EQ"
    ))
    

    relations.append((
        ["SET ex1 a", "SET ex2 b", "EXISTS ex1 ex2 ex3"],
        ["SET ex1 a", "EXISTS ex1"],
        "NE"
    ))
    

    relations.append((
        ["EVAL (if -1 100 200)"],
        ["EVAL 100"],
        "EQ"
    ))
    

    relations.append((
        ["SET cdecr 10", "DECR cdecr", "DECR cdecr", "DECR cdecr", "GET cdecr"],
        ["SET cdecr_res 7"],
        "EQ"
    ))
    

    relations.append((
        ["SET grange abc", "GETRANGE grange 0 0"],
        ["SET grange_res a"],
        "EQ"
    ))
    

    relations.append((
        ["SET m1 1", "SET m2 2", "SET m3 3", "CALC mres (+ $m1 $m2 $m3)", "GET mres"],
        ["SET mres_val 6"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrn 1 2 3 4 5", "LRANGE lrn -3 -1"],
        ["SET lrn_val 3 4 5"],
        "EQ"
    ))
    

    relations.append((
        ["SET lenm abc", "STRLEN lenm"],
        ["SET lenm_val 3"],
        "EQ"
    ))
    

    relations.append((
        ["DEL noexist1", "DEL noexist2"],
        ["DEL noexist3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpem 1 2 3 4 5", "LLEN lpem"],
        ["SET lpem_len 5"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ 5)"],
        ["EVAL 5"],
        "EQ"
    ))
    

    relations.append((
        ["SET emptyv ''", "GET emptyv"],
        ["SET emptyv2 ''"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lep 1", "LPOP lep", "LPOP lep"],
        ["LPOP lep2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (and (< 1 2) (> 3 2) (!= 1 0))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET vci 5", "INCR vci", "INCR vci", "GET vci"],
        ["SET vci_res 7"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrs 1 2 3", "LRANGE lrs 0 1"],
        ["LPUSH lrs2 3 2 1", "LRANGE lrs2 1 2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rev1 x", "LREV rev1", "LINDEX rev1 0"],
        ["SET rev1_val x"],
        "EQ"
    ))
    

    relations.append((
        ["SET app_e ''", "APPEND app_e x", "GET app_e"],
        ["SET app_e_res x"],
        "EQ"
    ))
    

    relations.append((
        ["SET ve 5", "EVAL (+ $ve $ve $ve)"],
        ["EVAL 15"],
        "EQ"
    ))
    

    relations.append((
        ["MSET ms_p a b c", "GET ms_p"],
        ["SET ms_p a"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (not (< 1 0))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET numt 123", "INCR numt", "DECR numt", "GET numt"],
        ["SET numt_res 123"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lmix 1", "LPUSH lmix 2", "LPOP lmix", "LLEN lmix"],
        ["SET lmix_len 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET subc abcdef", "GETRANGE subc 0 2"],
        ["SET subc_res abc"],
        "EQ"
    ))
    
    # 175. SET + DEL + SET
    relations.append((
        ["SET sds a", "DEL sds", "SET sds b", "GET sds"],
        ["SET sds2 b"],
        "EQ"
    ))
    

    relations.append((
        ["GET no_key_1"],
        ["GET no_key_2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpr 1 2 3", "LLEN lpr"],
        ["RPUSH rpr 1 2 3", "LLEN rpr"],
        "EQ"
    ))
    
    # 178. INCRBY 0
    relations.append((
        ["SET inc0 10", "INCRBY inc0 0", "GET inc0"],
        ["SET inc0_res 10"],
        "EQ"
    ))
    
    # 179. DECRBY 0
    relations.append((
        ["SET dec0 10", "DECRBY dec0 0", "GET dec0"],
        ["SET dec0_res 10"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if 1 (if 0 1 2) 3)"],
        ["EVAL 2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH revt a b c", "LREV revt", "LREV revt", "LRANGE revt 0 -1"],
        ["SET revt_res a b c"],
        "EQ"
    ))
    

    relations.append((
        ["SET m1 v1", "SET m2 v2", "MGET m1 m2"],
        ["SET m1 v1", "SET m2 v2", "GET m1"],
        "NE"
    ))
    

    relations.append((
        ["EVAL (/ 5 2)"],
        ["EVAL 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET mixns 123", "APPEND mixns abc", "GET mixns"],
        ["SET mixns_res 123abc"],
        "EQ"
    ))
    

    relations.append((
        ["LSET nlsk 0 x"],
        ["LSET nlsk2 0 y"],
        "EQ"
    ))
    

    relations.append((
        ["SET ed a", "EXISTS ed", "DEL ed", "EXISTS ed"],
        ["EXISTS ed2"],
        "NE"
    ))
    

    relations.append((
        ["SET v1 10", "SET v2 5", "EVAL (- $v1 $v2)"],
        ["EVAL 5"],
        "EQ"
    ))
    

    relations.append((
        ["SET mapa a", "APPEND mapa b", "APPEND mapa c", "APPEND mapa d", "GET mapa"],
        ["SET mapa_res abcd"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (< 10 20) 1 0)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lop 1 2", "LLEN lop", "LPUSH lop 3", "LLEN lop"],
        ["SET lop_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["LPOP empty_lp"],
        ["RPOP empty_rp"],
        "EQ"
    ))
    

    relations.append((
        ["SET slen a", "STRLEN slen", "APPEND slen bc", "STRLEN slen"],
        ["SET slen_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET eqc 100", "EVAL (== $eqc 100)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrdo 1 2 3", "LRANGE lrdo 0 1"],
        ["SET lrdo_res 1 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET type1 1", "LPUSH type2 2", "LLEN type1"],
        ["LLEN type2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ (/ 7 3) (/ 8 3))"],
        ["EVAL 4"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsetm 1 2 3", "LSET lsetm 0 9", "LSET lsetm 1 9", "LSET lsetm 2 9", "LRANGE lsetm 0 -1"],
        ["SET lsetm_res 9 9 9"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lvn 1 2 3", "LLEN lvn"],
        ["SET lvn_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET ag a", "APPEND ag b", "APPEND ag c", "GET ag"],
        ["SET ag_res abc"],
        "EQ"
    ))
    

    relations.append((
        ["SET ce1 2", "SET ce2 3", "SET ce3 4", "EVAL (+ (* $ce1 $ce1) (* $ce2 $ce2) (* $ce3 $ce3))"],
        ["EVAL 29"],
        "EQ"
    ))
    

    relations.append((
        ["SET d1 a", "SET d2 b", "SET d3 c", "DEL d1 d2 d3", "EXISTS d1"],
        ["EXISTS d3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrng_o 1 2 3", "LRANGE lrng_o 5 10"],
        ["LPUSH lrng_o2 1 2 3", "LRANGE lrng_o2 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["SET strlst abc", "LPUSH lstlst 1 2 3", "STRLEN strlst"],
        ["LLEN lstlst"],
        "NE"
    ))
    

    relations.append((
        ["SET vo1 10", "SET vo2 5", "EVAL (* $vo1 $vo2)"],
        ["EVAL 50"],
        "EQ"
    ))
    

    relations.append((
        ["SET id a", "INCR id", "DEL id", "EXISTS id"],
        ["EXISTS id2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpa 1 2", "LPUSH lpa 3", "LPOP lpa", "LLEN lpa"],
        ["SET lpa_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET sn 123", "INCR sn", "DECR sn", "GET sn"],
        ["SET sn_res 123"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrli 1 2 3", "LREV lrli", "LINDEX lrli 0"],
        ["SET lrli_val 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET grp abcde", "GETRANGE grp 1 3"],
        ["SET grp_val bc"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 1 0)"],
        ["SET x 1", "INCR x", "DECR x", "EVAL (/ $x 0)"],
        "EQ"
    ))
    

    relations.append((
        ["SET exk v", "EXISTS exk"],
        ["SET exk2 v2", "EXISTS exk2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpo a b c", "LRANGE lpo 0 -1"],
        ["SET lpo_res a b c"],
        "EQ"
    ))
    

    relations.append((
        ["SET msx a", "SET msx b", "SET msx c", "GET msx"],
        ["SET msx c"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (+ $undef_x 1)"],
        ["EVAL (* $undef_y 2)"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lmho 1 2 3", "LPOP lmho", "LPUSH lmho 4", "LLEN lmho"],
        ["SET lmho_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET cvc 1", "CALC cvr (+ $cvc 1)", "CALC cvr (+ $cvr 1)", "GET cvr"],
        ["CALC cvr2 (+ 1 1 1)", "GET cvr2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (not (and (or 0 0) (not 1)))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsi 1 2 3", "LSET lsi 1 9", "LINDEX lsi 1"],
        ["SET lsi_val 9"],
        "EQ"
    ))
    

    relations.append((
        ["SET sl2 abc", "STRLEN sl2"],
        ["SET sl2_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET vc1 10", "SET vc2 20", "EVAL (< $vc1 $vc2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["RPUSH rpo a b c", "LRANGE rpo 0 -1"],
        ["SET rpo_res a b c"],
        "EQ"
    ))
    
    # 222. SET + INCR
    relations.append((
        ["SET si 5", "INCR si", "GET si"],
        ["SET si_res 6"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrtl 1 2 3 4", "LREV lrtl", "LLEN lrtl"],
        ["SET lrtl_len 4"],
        "EQ"
    ))
    

    relations.append((
        ["SET m1 v1", "MGET m1"],
        ["SET m1 v1", "GET m1"],
        "EQ"
    ))
    

    relations.append((
        ["SET sl3 abcdef", "STRLEN sl3"],
        ["SET sl3_len 6"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lge 1 2 3", "GET lge"],
        ["SET lge2 1 2 3", "GET lge2"],
        "EQ"
    ))
    

    relations.append((
        ["SET eva 5", "SET evb 3", "EVAL (+ $eva $evb)"],
        ["EVAL 8"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrfe a b a", "LREM lrfe 0 a", "LLEN lrfe"],
        ["SET lrfe_len 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET se a", "SET se ''", "GET se"],
        ["SET se2 ''"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if 0 1 (if 1 2 3))"],
        ["EVAL 2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lprp a b c", "RPOP lprp"],
        ["SET lprp_val a"],
        "EQ"
    ))
    

    relations.append((
        ["SET ini 0", "INCR ini", "INCR ini", "GET ini"],
        ["SET ini_res 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET grn abc", "GETRANGE grn -2 -1"],
        ["SET grn_val bc"],
        "EQ"
    ))
    

    relations.append((
        ["SET vo3 6", "SET vo4 2", "EVAL (/ $vo3 $vo4)"],
        ["EVAL 3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrft 1 2 3", "LRANGE lrft 0 0"],
        ["SET lrft_val 1"],
        "EQ"
    ))
    

    relations.append((
        ["EXISTS newk"],
        ["EXISTS newk2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsg 1 2", "GET lsg"],
        ["SET lsg2 1 2", "GET lsg2"],
        "EQ"
    ))
    

    relations.append((
        ["SET co1 2", "SET co2 3", "SET co3 4", "EVAL (* (+ $co1 $co2) $co3)"],
        ["EVAL 20"],
        "EQ"
    ))
    

    relations.append((
        ["SET dk a", "DEL dk", "EXISTS dk"],
        ["EXISTS nokey"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsle 1 2 3", "LSET lsle -1 9", "LINDEX lsle -1"],
        ["SET lsle_val 9"],
        "EQ"
    ))
    

    relations.append((
        ["SET snum 100", "APPEND snum 0", "GET snum"],
        ["SET snum_res 1000"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (and (not 0) (< 1 2))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpll 1 2", "LPUSH lpll 3", "LLEN lpll"],
        ["SET lpll_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET evs1 10", "SET evs2 3", "EVAL (- $evs1 $evs2)"],
        ["EVAL 7"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrngn 1 2 3 4 5", "LRANGE lrngn -3 -2"],
        ["SET lrngn_val 3 4"],
        "EQ"
    ))
    

    relations.append((
        ["SET ineg -5", "INCR ineg"],
        ["SET ineg_res -4"],
        "EQ"
    ))
    

    relations.append((
        ["SET sco a", "SET sco b", "GET sco"],
        ["SET sco b"],
        "EQ"
    ))
    

    relations.append((
        ["SET vc1 10", "EVAL (+ $vc1 $vc1 $vc1 $vc1)"],
        ["EVAL 40"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrngv 1 2 3", "LREV lrngv", "LRANGE lrngv 0 1"],
        ["SET lrngv_val 3 2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 9 2)"],
        ["EVAL 4"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH ldel 1 2 3", "LREM ldel 0 2", "LLEN ldel"],
        ["SET ldel_len 2"],
        "EQ"
    ))
    
    # 252. STRLEN 0
    relations.append((
        ["SET sz ''", "STRLEN sz"],
        ["SET sz_len 0"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpm 1 2 3", "LPOP lpm", "LPOP lpm", "GET lpm"],
        ["SET lpm_val 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET vn 50", "EVAL (+ $vn $vn $vn)"],
        ["EVAL 150"],
        "EQ"
    ))
    

    relations.append((
        ["SET exm 1", "EXISTS exm", "EXISTS exm"],
        ["SET exm2 1", "EXISTS exm2"],
        "EQ"
    ))
    

    relations.append((
        ["SET apl 1", "APPEND apl 2", "APPEND apl 3", "APPEND apl 4", "STRLEN apl"],
        ["SET apl_len 4"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrc 1 2 3", "LREV lrc"],
        ["LPUSH lrc2 3 2 1", "LREV lrc2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrall 1 2 3", "LRANGE lrall 0 -1"],
        ["SET lrall_val 1 2 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET sc1 hello", "SET sc2 hello", "EVAL (== $sc1 $sc2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET vo1 5", "SET vo2 3", "SET vo3 2", "EVAL (+ (* $vo1 $vo2) $vo3)"],
        ["EVAL 17"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsex 1 2 3", "LSET lsex 0 9", "GET lsex"],
        ["SET lsex2 9 2 3", "GET lsex2"],
        "NE"
    ))
    

    relations.append((
        ["CALC calc1 (+ 1 2 3)", "GET calc1"],
        ["SET calc1_res 6"],
        "EQ"
    ))
    

    relations.append((
        ["SET svn 999", "INCR svn"],
        ["SET svn_res 1000"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpp a b c", "LPOP lpp"],
        ["SET lpp_val c"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ -10 3)"],
        ["EVAL -3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lark 1 2", "EXISTS lark"],
        ["SET lark2 1 2", "EXISTS lark2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (if 0 1 0) (if 1 100 200) (if 0 300 400))"],
        ["EVAL 400"],
        "EQ"
    ))
    

    relations.append((
        ["MSET mso a 1 b 2", "SET b 3", "GET b"],
        ["SET b 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET ib 0", "INCRBY ib 100"],
        ["SET ib_res 100"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrev_even 1 2 3 4", "LREV lrev_even"],
        ["LPUSH lrev_even2 4 3 2 1", "LREV lrev_even2"],
        "EQ"
    ))
    

    relations.append((
        ["SET slg ''", "APPEND slg a", "APPEND slg b", "STRLEN slg"],
        ["SET slg_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET veq 100", "EVAL (== $veq 100)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET d1 1", "SET d2 2", "DEL d1 d2", "EXISTS d1"],
        ["SET d3 3", "DEL d3", "EXISTS d3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrng_o2 1 2 3", "LRANGE lrng_o2 0 10"],
        ["LPUSH lrng_o3 1 2 3", "LRANGE lrng_o3 0 -1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrdel 1 2 3", "LREM lrdel 0 2", "LLEN lrdel"],
        ["SET lrdel_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET snv 42", "GET snv"],
        ["SET snv_res 42"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (not (not (not 0)))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH rpm 1 2 3", "RPOP rpm", "RPOP rpm"],
        ["SET rpm_res 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET ve1 7", "SET ve2 3", "EVAL (% $ve1 $ve2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET spc a", "APPEND spc b", "APPEND spc c", "GET spc"],
        ["SET spc_res abc"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpd 1", "LPUSH lpd 2", "LPUSH lpd 3", "LRANGE lpd 0 -1"],
        ["SET lpd_val 3 2 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET db 10", "DECRBY db 3"],
        ["SET db_res 7"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsfe 1 2 3", "LSET lsfe 0 9", "LINDEX lsfe 0"],
        ["SET lsfe_val 9"],
        "EQ"
    ))
    

    relations.append((
        ["SET snm 1", "APPEND snm a", "STRLEN snm"],
        ["SET snm_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if 1 (if 1 10 20) 30)"],
        ["EVAL 10"],
        "EQ"
    ))
    

    relations.append((
        ["MSET mso2 a 1 b 2 c 3", "MGET a b c"],
        ["SET a a", "SET b b", "SET c c", "MGET a b c"],
        "NE"
    ))
    

    relations.append((
        ["LPUSH lr_sw 1 2 3", "LRANGE lr_sw 0 1"],
        ["SET lr_sw_val 1 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET inn abc", "INCR inn"],
        ["SET inn2 abc", "DECR inn2"],
        "EQ"
    ))
    

    relations.append((
        ["SET vo5 10", "EVAL (+ $vo5 $vo5)"],
        ["EVAL 20"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrga 1 2 3", "LREV lrga", "GET lrga"],
        ["SET lrga2 3 2 1", "GET lrga2"],
        "EQ"
    ))
    

    relations.append((
        ["SET slc hello", "STRLEN slc"],
        ["SET slc_len 5"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH le2 1", "EXISTS le2"],
        ["SET le22 1", "EXISTS le22"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (or (and 1 1) 0)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET scd a", "DEL scd", "SET scd b", "EXISTS scd"],
        ["SET scd2 b", "EXISTS scd2"],
        "EQ"
    ))
    

    relations.append((
        ["SET vc1 5", "EVAL (if (< $vc1 10) 1 0)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH llw 1 2", "LLEN llw", "LPUSH llw 3", "LLEN llw"],
        ["LPUSH llw2 1 2 3", "LLEN llw2"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (/ 20 6)"],
        ["EVAL 3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrm 1 2 3 4", "LRANGE lrm 1 2"],
        ["SET lrm_val 2 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET vs1 100", "SET vs2 30", "EVAL (- $vs1 $vs2)"],
        ["EVAL 70"],
        "EQ"
    ))
    

    relations.append((
        ["SET ape ''", "APPEND ape x", "GET ape"],
        ["SET ape_res x"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH ld2 a b a", "LREM ld2 1 a", "LLEN ld2"],
        ["SET ld2_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET smv1 a", "SET smv2 b", "SET smv1 c", "GET smv1"],
        ["SET smv1 c"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (or (< 1 0) (> 2 1))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lpg a b c", "LPOP lpg", "GET lpg"],
        ["SET lpg_val a b"],
        "EQ"
    ))
    

    relations.append((
        ["SET vm1 6", "SET vm2 7", "EVAL (* $vm1 $vm2)"],
        ["EVAL 42"],
        "EQ"
    ))
    

    relations.append((
        ["SET is1 5", "INCR is1", "SET is1 10", "GET is1"],
        ["SET is1_res 10"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrf a b c", "LRANGE lrf 0 -1"],
        ["SET lrf_val a b c"],
        "EQ"
    ))
    

    relations.append((
        ["SET seqs1 abc", "SET seqs2 abc", "EVAL (== $seqs1 $seqs2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lmx 1 2", "LPUSH lmx 3", "LPOP lmx", "LLEN lmx"],
        ["SET lmx_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET de2 a", "DEL de2", "EXISTS de2"],
        ["EXISTS noexist3"],
        "EQ"
    ))
    

    relations.append((
        ["SET va1 5", "SET va2 10", "EVAL (+ $va1 $va2)"],
        ["EVAL 15"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsg2 1 2 3", "LSET lsg2 1 9", "GET lsg2"],
        ["SET lsg22 1 9 3", "GET lsg22"],
        "NE"
    ))
    

    relations.append((
        ["EVAL (% 17 5)"],
        ["EVAL 2"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lri 1 2 3", "LREV lri", "LINDEX lri 0"],
        ["SET lri_val 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET ag2 a", "APPEND ag2 b", "GET ag2"],
        ["SET ag2_res ab"],
        "EQ"
    ))
    

    relations.append((
        ["SET im 0", "INCR im", "INCR im", "INCR im", "GET im"],
        ["SET im_res 3"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (if (if 1 0 1) (if 0 100 200) 300)"],
        ["EVAL 300"],
        "EQ"
    ))
    

    relations.append((
        ["SET slg2 ''", "APPEND slg2 abc", "STRLEN slg2"],
        ["SET slg2_len 3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lps a", "LLEN lps"],
        ["SET lps_len 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET vne1 10", "SET vne2 20", "EVAL (!= $vne1 $vne2)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["SET grn2 abcde", "GETRANGE grn2 -3 -1"],
        ["SET grn2_val cde"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrd2 a b c", "LREM lrd2 0 b", "LLEN lrd2"],
        ["SET lrd2_len 2"],
        "EQ"
    ))
    

    relations.append((
        ["SET smh 123", "APPEND smh abc", "GET smh"],
        ["SET smh_res 123abc"],
        "EQ"
    ))
    

    relations.append((
        ["SET vcr1 5", "SET vcr2 10", "EVAL (> $vcr2 $vcr1)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrall2 1 2 3", "LRANGE lrall2 0 100"],
        ["SET lrall2_val 1 2 3"],
        "EQ"
    ))
    

    relations.append((
        ["SET inv -10", "INCR inv"],
        ["SET inv_res -9"],
        "EQ"
    ))
    

    relations.append((
        ["SET scv 1", "SET scv 2", "SET scv 3", "GET scv"],
        ["SET scv3 3"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrfst 5 4 3 2 1", "LRANGE lrfst 0 0"],
        ["SET lrfst_val 5"],
        "EQ"
    ))
    

    relations.append((
        ["SET vcg 10", "EVAL (if (> $vcg 5) 1 0)"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH ll2 1 2 3 4 5", "LLEN ll2"],
        ["SET ll2_len 5"],
        "EQ"
    ))
    

    relations.append((
        ["SET sn2 999", "INCR sn2"],
        ["SET sn2_res 1000"],
        "EQ"
    ))
    

    relations.append((
        ["EVAL (and (< 5 10) (> 3 1))"],
        ["EVAL 1"],
        "EQ"
    ))
    

    relations.append((
        ["RPUSH rpo2 a b c", "RPOP rpo2"],
        ["SET rpo2_val c"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lsm 1 2 3", "LSET lsm 2 9", "LINDEX lsm 2"],
        ["SET lsm_val 9"],
        "EQ"
    ))
    

    relations.append((
        ["SET vd1 20", "SET vd2 4", "EVAL (/ $vd1 $vd2)"],
        ["EVAL 5"],
        "EQ"
    ))
    

    relations.append((
        ["SET sle ''", "STRLEN sle"],
        ["SET sle_len 0"],
        "EQ"
    ))
    

    relations.append((
        ["LPOP lpe"],
        ["RPOP lpe2"],
        "EQ"
    ))
    

    relations.append((
        ["SET ss2 hello", "GET ss2"],
        ["SET ss2_res hello"],
        "EQ"
    ))
    

    relations.append((
        ["SET is2 100", "INCR is2", "DECR is2", "GET is2"],
        ["SET is2_res 100"],
        "EQ"
    ))
    

    relations.append((
        ["LPUSH lrdbl 1 2 3", "LREV lrdbl", "LREV lrdbl"],
        ["LPUSH lrdbl2 1 2 3", "LREV lrdbl2"],
        "EQ"
    ))
    
    return relations

