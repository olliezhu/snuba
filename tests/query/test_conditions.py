from snuba.query.conditions import binary_condition, BooleanFunctions, ComparisonsFunctions
from snuba.query.expressions import AliasedExpression, FunctionCall, Column, Expression


def test_expressions_from_basic_condition() -> None:
    """
    Iterates over the expressions in a basic condition
    """

    c = Column("c1", "t1")
    f1 = FunctionCall("f", [c])
    c2 = Column("c2", "t1")

    condition = binary_condition(ComparisonsFunctions.EQ, f1, c2)
    ret = list(condition)
    expected = [condition, f1, c, c2]

    assert ret == expected


def test_aliased_expressions_from_basic_condition() -> None:
    """
    Iterates over the expressions in a basic condition when those expressions
    are aliased
    """

    c = Column("c1", "t1")
    f1 = FunctionCall("f", [c])
    al1 = AliasedExpression("a", f1)
    c2 = Column("c2", "t1")
    al2 = AliasedExpression("a", c2)

    condition = binary_condition(ComparisonsFunctions.EQ, al1, al2)
    ret = list(condition)
    expected = [condition, al1, f1, c, al2, c2]

    assert ret == expected


def test_map_expressions_in_basic_condition() -> None:
    """
    Change the column name over the expressions in a basic condition
    """
    c = Column("c1", "t1")
    f1 = FunctionCall("f", [c])
    c2 = Column("c2", "t1")

    c3 = Column("c3", "t1")

    def replace_col(e: Expression) -> Expression:
        if isinstance(e, Column) and e.column_name == "c1":
            return c3
        return e

    condition = binary_condition(ComparisonsFunctions.EQ, f1, c2)
    condition.transform(replace_col)
    ret = list(condition)
    expected = [condition, f1, c3, c2]

    assert ret == expected


def test_nested_simple_condition() -> None:
    """
    Iterates and maps expressions over a complex Condition:
    (A=B OR A=B) AND (A=B OR A=B)
    """

    c1 = Column("c1", "t1")
    c2 = Column("c2", "t1")
    co1 = binary_condition(ComparisonsFunctions.EQ, c1, c2)

    c3 = Column("c1", "t1")
    c4 = Column("c2", "t1")
    co2 = binary_condition(ComparisonsFunctions.EQ, c3, c4)
    or1 = binary_condition(BooleanFunctions.OR, co1, co2)

    c5 = Column("c1", "t1")
    c6 = Column("c2", "t1")
    co4 = binary_condition(ComparisonsFunctions.EQ, c5, c6)

    c7 = Column("c1", "t1")
    c8 = Column("c2", "t1")
    co5 = binary_condition(ComparisonsFunctions.EQ, c7, c8)
    or2 = binary_condition(BooleanFunctions.OR, co4, co5)
    and1 = binary_condition(BooleanFunctions.AND, or1, or2)

    ret = list(and1)
    expected = [and1, or1, co1, c1, c2, co2, c3, c4, or2, co4, c5, c6, co5, c7, c8]
    assert ret == expected

    cX = Column("cX", "t1")

    def replace_col(e: Expression) -> Expression:
        if isinstance(e, Column) and e.column_name == "c2":
            return cX
        return e

    and1.transform(replace_col)
    ret = list(and1)
    expected = [and1, or1, co1, c1, cX, co2, c3, cX, or2, co4, c5, cX, co5, c7, cX]
    assert ret == expected