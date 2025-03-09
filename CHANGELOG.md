# Changelog

## v0.1.6 (2025-03-09)
- Stable beta release

### Feature
- Add Logger `class SNAPLogger`
- Auto parse Exception.  
  Now we can simply, eg. `raise InvalidAmount()` instead of parsing error message  
  to comply SNAP Status Response.  
  Default Exception is `class InternalServerError`.

### Fix
- Bugfix `class SNAPException`
- Bugfix `routing.py`


## v0.1.0 - v0.1.5 (2025-03-07)
- First alpha releases