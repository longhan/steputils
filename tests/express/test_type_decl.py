# Copyright (c) 2020 Manfred Moitzi
# License: MIT License

import pytest
from steputils.express.parser import type_decl, where_clause
from steputils.express.ast import AST


def test_typedef_real():
    r = AST(type_decl.parseString('TYPE IfcAbsorbedDoseMeasure = REAL;END_TYPE;'))
    assert str(r) == 'TYPE IfcAbsorbedDoseMeasure = REAL ; END_TYPE ;'


def test_typedef_list():
    r = AST(type_decl.parseString('TYPE IfcArcIndex = LIST [3:3] OF IfcPositiveInteger;END_TYPE;'))
    assert str(r) == 'TYPE IfcArcIndex = LIST [ 3 : 3 ] OF IfcPositiveInteger ; END_TYPE ;'


def test_typedef_enum():
    t = AST(type_decl.parseString("""
    TYPE IfcActionRequestTypeEnum = ENUMERATION OF
        (EMAIL,
        FAX,
        PHONE,
        POST,
        VERBAL,
        USERDEFINED,
        NOTDEFINED);
    END_TYPE;
    """))
    assert str(t) == "TYPE IfcActionRequestTypeEnum = ENUMERATION OF " \
                     "( EMAIL , FAX , PHONE , POST , VERBAL , USERDEFINED , NOTDEFINED ) ; " \
                     "END_TYPE ;"


def test_typedef_select():
    t = AST(type_decl.parseString("""
    TYPE IfcValue = SELECT (
        IfcDerivedMeasureValue,
        IfcMeasureValue,
        IfcSimpleValue);
    END_TYPE;
    """))
    assert str(t) == "TYPE IfcValue = SELECT ( IfcDerivedMeasureValue , IfcMeasureValue , IfcSimpleValue ) ; END_TYPE ;"


def test_where_clause_0():
    r = AST(where_clause.parseString("WHERE SELF > 0;"))
    assert str(r) == "WHERE SELF > 0 ;"


def test_where_clause_1():
    r = AST(where_clause.parseString("WHERE GreaterThanZero : SELF > 0;"))
    assert str(r) == "WHERE GreaterThanZero : SELF > 0 ;"


def test_where_clause_2():
    r = AST(where_clause.parseString(" WHERE SELF IN ['left', 'middle'];"))
    assert str(r) == "WHERE SELF IN [ left , middle ] ;"
    r = AST(where_clause.parseString(" WHERE WR1 : SELF IN ['left', 'middle'];"))
    assert str(r) == "WHERE WR1 : SELF IN [ left , middle ] ;"


def test_where_clause_3():
    r = AST(where_clause.parseString("WHERE SELF > 0; SELF < 2;"))
    assert str(r) == "WHERE SELF > 0 ; SELF < 2 ;"


def test_where_clause_4():
    r = AST(where_clause.parseString("WHERE SELF > 0; SELF < 2; END_TYPE;"))
    assert str(r) == "WHERE SELF > 0 ; SELF < 2 ;", 'should ignore: END_TYPE;'


def test_where_clause_5():
    r = AST(where_clause.parseString("WHERE MinutesInRange : ABS(SELF[2]) < 60;"))
    assert str(r) == "WHERE MinutesInRange : ABS ( SELF [ 2 ] ) < 60 ;"


def test_where_rule_0():
    r = AST(type_decl.parseString("TYPE XType = INTEGER; WHERE SELF > 0; END_TYPE;"))
    assert str(r) == "TYPE XType = INTEGER ; WHERE SELF > 0 ; END_TYPE ;"


def test_where_rule_1():
    r = AST(type_decl.parseString("""
    TYPE IfcCardinalPointReference = INTEGER;
    WHERE
        GreaterThanZero : SELF > 0;
    END_TYPE;
    """))

    assert str(r) == "TYPE IfcCardinalPointReference = INTEGER ; WHERE GreaterThanZero : SELF > 0 ; END_TYPE ;"


def test_where_rule_2():
    r = AST(type_decl.parseString("""
    TYPE IfcCompoundPlaneAngleMeasure = LIST [3:4] OF INTEGER;
        WHERE
        MinutesInRange : ABS(SELF[2]) < 60;
        SecondsInRange : ABS(SELF[3]) < 60;
        MicrosecondsInRange : (SIZEOF(SELF) = 3) OR (ABS(SELF[4]) < 1000000);
        ConsistentSign : ((SELF[1] >= 0) AND (SELF[2] >= 0) AND (SELF[3] >= 0) AND ((SIZEOF(SELF) = 3) OR (SELF[4] >= 0)))
        OR
        ((SELF[1] <= 0) AND (SELF[2] <= 0) AND (SELF[3] <= 0) AND ((SIZEOF(SELF) = 3) OR (SELF[4] <= 0)));
    END_TYPE;
    """))
    assert len(r) == 162


if __name__ == '__main__':
    pytest.main([__file__])
