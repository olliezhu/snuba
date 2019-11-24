from typing import Optional, Sequence
from snuba.query.expressions import (
    Column,
    CurriedFunctionCall,
    Expression,
    ExpressionVisitor,
    FunctionCall,
    Literal,
)
from snuba.query.parsing import ParsingContext
from snuba.util import escape_col

# Tokens used when formatting. Defining them as costant
# will make it easy (if/when needed) to make some changes
# to the layout of the output.
NULL = "NULL"
COMMA = ","
SPACE = " "
TRUE = "true"
FALSE = "false"
QUOTE = "'"
OPEN_BRACKET = "("
CLOSED_BRACKET = ")"
DOT = "."


class ClickhouseExpressionFormatter(ExpressionVisitor[str]):
    """
    This Visitor implementation is able to format one expression in the Snuba
    Query for Clickhouse.

    The only state mainained is the PrasingContext, which allows us to resolve
    aliases and can be reused when formatting multiple expressions.

    When passing an instance of this class to the accept method of
    the visited expression, the return value is the formatted string.
    """

    def __init__(self, parsing_context: Optional[ParsingContext] = None) -> None:
        self.__parsing_context = parsing_context or ParsingContext()

    def __escape(self, column: str) -> str:
        return escape_col(column)

    def __alias(self, formatted_exp: str, alias: Optional[str]) -> str:
        if not alias:
            return formatted_exp
        elif self.__parsing_context.is_alias_present(alias):
            return alias
        else:
            self.__parsing_context.add_alias(alias)
            return (
                f"{OPEN_BRACKET}{formatted_exp}{SPACE}AS{SPACE}{alias}{CLOSED_BRACKET}"
            )

    def visitLiteral(self, exp: Literal) -> str:
        if exp.value is None:
            return NULL
        elif exp.value is True:
            return TRUE
        elif exp.value is False:
            return FALSE
        elif isinstance(exp.value, str):
            return f"{QUOTE}{exp.value}{QUOTE}"
        elif isinstance(exp.value, (int, float)):
            return str(exp.value)
        else:
            raise ValueError(f"Invalid literal type {type(exp.value)}")

    def visitColumn(self, exp: Column) -> str:
        ret = []
        if exp.table_name:
            ret.append(self.__escape(exp.table_name))
            ret.append(DOT)
        ret.append(self.__escape(exp.column_name))
        return self.__alias("".join(ret), exp.alias)

    def __visit_params(self, parameters: Sequence[Expression]) -> str:
        ret = [p.accept(self) for p in parameters]
        param_list = ", ".join(ret)
        return f"{OPEN_BRACKET}{param_list}{CLOSED_BRACKET}"

    def visitFunctionCall(self, exp: FunctionCall) -> str:
        ret = f"{exp.function_name}{self.__visit_params(exp.parameters)}"
        return self.__alias(ret, exp.alias)

    def visitCurriedFunctionCall(self, exp: CurriedFunctionCall) -> str:
        int_func = exp.internal_function.accept(self)
        ret = f"{int_func}{self.__visit_params(exp.parameters)}"
        return self.__alias(ret, exp.alias)