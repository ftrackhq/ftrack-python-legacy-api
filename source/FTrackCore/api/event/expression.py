# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

from operator import eq, ne, ge, le, gt, lt

from pyparsing import (ParserElement, Group, Word, CaselessKeyword, Forward,
                       FollowedBy, Suppress, oneOf, OneOrMore, Optional,
                       alphanums, quotedString, removeQuotes)

from ..ftrackerror import ParseError

# Optimise parsing using packrat memoisation feature.
ParserElement.enablePackrat()


class Parser(object):
    '''Parse string based expression into :py:class:`Expression` instance.'''

    def __init__(self):
        '''Initialise parser.'''
        self._operators = {
            '=': eq,
            '!=': ne,
            '>=': ge,
            '<=': le,
            '>': gt,
            '<': lt
        }
        self._parser = self._constructParser()
        super(Parser, self).__init__()

    def _constructParser(self):
        '''Construct and return parser.'''
        field = Word(alphanums + '_.')
        operator = oneOf(self._operators.keys())
        value = Word(alphanums + '-_,./*@+')
        quotedValue = quotedString('quotedValue').setParseAction(removeQuotes)

        condition = Group(field + operator + (quotedValue | value))('condition')

        not_ = Optional(Suppress(CaselessKeyword('not')))('not')
        and_ = Suppress(CaselessKeyword('and'))('and')
        or_ = Suppress(CaselessKeyword('or'))('or')

        expression = Forward()
        parenthesis = Suppress('(') + expression + Suppress(')')
        previous = condition | parenthesis

        for conjunction in (not_, and_, or_):
            current = Forward()

            if conjunction in (and_, or_):
                conjunctionExpression = (
                    FollowedBy(previous + conjunction + previous)
                    + Group(
                        previous + OneOrMore(conjunction + previous)
                    )(conjunction.resultsName)
                )

            elif conjunction in (not_, ):
                conjunctionExpression = (
                    FollowedBy(conjunction.expr + current)
                    + Group(conjunction + current)(conjunction.resultsName)
                )

            else:
                raise ValueError('Unrecognised conjunction.')

            current <<= (conjunctionExpression | previous)
            previous = current

        expression <<= previous
        return expression('expression')

    def parse(self, expression):
        '''Parse string *expression* into :py:class:`Expression`.

        Raise :py:exc:`ftrack.ParseError` if *expression* could not be parsed.

        '''
        result = None
        expression = expression.strip()
        if expression:
            try:
                result = self._parser.parseString(
                    expression, parseAll=True
                )
            except Exception as error:
                raise ParseError(
                    'Failed to parse: {0}. {1}'.format(expression, error)
                )

        return self._process(result)

    def _process(self, result):
        '''Process *result* using appropriate method.

        Method called is determined by the name of the result.

        '''
        methodName = '_process{0}'.format(result.getName().title())
        method = getattr(self, methodName)
        return method(result)

    def _processExpression(self, result):
        '''Process *result* as expression.'''
        return self._process(result[0])

    def _processNot(self, result):
        '''Process *result* as NOT operation.'''
        return Not(self._process(result[0]))

    def _processAnd(self, result):
        '''Process *result* as AND operation.'''
        return All([self._process(entry) for entry in result])

    def _processOr(self, result):
        '''Process *result* as OR operation.'''
        return Any([self._process(entry) for entry in result])

    def _processCondition(self, result):
        '''Process *result* as condition.'''
        key, operator, value = result
        return Condition(key, self._operators[operator], value)

    def _processQuotedValue(self, result):
        '''Process *result* as quoted value.'''
        return result


class Expression(object):
    '''Represent a structured expression to test candidates against.'''

    def __str__(self):
        '''Return string representation.'''
        return '<{0}>'.format(self.__class__.__name__)

    def match(self, candidate):
        '''Return whether *candidate* satisfies this expression.'''
        return True


class All(Expression):
    '''Match candidate that matches all of the specified expressions.'''

    def __init__(self, expressions=None):
        '''Initialise with list of *expressions* to match against.'''
        self._expressions = expressions or []
        super(All, self).__init__()

    def __str__(self):
        '''Return string representation.'''
        return '<{0} [{1}]>'.format(
            self.__class__.__name__,
            ' '.join(map(str, self._expressions))
        )

    def match(self, candidate):
        '''Return whether *candidate* satisfies this expression.'''
        return all([
            expression.match(candidate) for expression in self._expressions
        ])


class Any(Expression):
    '''Match candidate that matches any of the specified expressions.'''

    def __init__(self, expressions=None):
        '''Initialise with list of *expressions* to match against.'''
        self._expressions = expressions or []
        super(Any, self).__init__()

    def __str__(self):
        '''Return string representation.'''
        return '<{0} [{1}]>'.format(
            self.__class__.__name__,
            ' '.join(map(str, self._expressions))
        )

    def match(self, candidate):
        '''Return whether *candidate* satisfies this expression.'''
        return any([
            expression.match(candidate) for expression in self._expressions
        ])


class Not(Expression):
    '''Negate expression.'''

    def __init__(self, expression):
        '''Initialise with *expression* to negate.'''
        self._expression = expression
        super(Not, self).__init__()

    def __str__(self):
        '''Return string representation.'''
        return '<{0} {1}>'.format(
            self.__class__.__name__,
            self._expression
        )

    def match(self, candidate):
        '''Return whether *candidate* satisfies this expression.'''
        return not self._expression.match(candidate)


class Condition(Expression):
    '''Represent condition.'''

    def __init__(self, key, operator, value):
        '''Initialise condition.

        *key* is the key to check on the data when matching. It can be a nested
        key represented by dots. For example, 'data.eventType' would attempt to
        match candidate['data']['eventType']. If the candidate is missing any
        of the requested keys then the match fails immediately.

        *operator* is the operator function to use to perform the match between
        the retrieved candidate value and the conditional *value*.

        If *value* is a string, it can use a wildcard '*' at the end to denote
        that any values matching the substring portion are valid when matching
        equality only.

        '''
        self._key = key
        self._operator = operator
        self._value = value
        self._wildcard = '*'
        self._operatorMapping = {
            eq: '=',
            ne: '!=',
            ge: '>=',
            le: '<=',
            gt: '>',
            lt: '<'
        }

    def __str__(self):
        '''Return string representation.'''
        return '<{0} {1}{2}{3}>'.format(
            self.__class__.__name__,
            self._key,
            self._operatorMapping.get(self._operator, self._operator),
            self._value
        )

    def match(self, candidate):
        '''Return whether *candidate* satisfies this expression.'''
        keyParts = self._key.split('.')

        try:
            value = candidate
            for keyPart in keyParts:
                value = value[keyPart]
        except (KeyError, TypeError):
            return False

        if (
            self._operator is eq
            and isinstance(self._value, basestring)
            and self._value[-1] == self._wildcard
        ):
            return self._value[:-1] in value
        else:
            return self._operator(value, self._value)
