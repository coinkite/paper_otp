Paper OTP
=========

Paper OTP Code generator
------------------------

Manage a single-page PDF containing single-use numeric tokens. The tokens
are generated using the RFC6238 algorithm with the X/Y coordinate as
the interval number. The "secret" seed values used here are base32-encoded
strings of length 16.

When deploying this, it's important to never use the same code twice. It's 
probably best to pick randomly from the set of codes you've never asked for.

See the example files:

- [Example PDF file](example.pdf)
- [Example text file](example.txt)
