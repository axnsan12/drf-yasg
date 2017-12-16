#########
Changelog
#########


*********
**1.0.4**
*********

- **FIX:** fixed improper generation of YAML references
- **FEATURE:** added ``query_serializer`` parameter to
  :func:`@swagger_auto_schema <.swagger_auto_schema>` (:issue:`16`, :pr:`17`)

*********
**1.0.3**
*********

- **FIX:** fixed bug that caused schema views returned from cache to fail (:issue:`14`)
- **FIX:** disabled automatic generation of response schemas for form operations to avoid confusing errors caused by
  attempting to shove file parameters into Schema objects

*********
**1.0.2**
*********

- First published version
