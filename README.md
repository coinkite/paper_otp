# Paper OTP

## Paper OTP Code Generator

Manage a single-page PDF containing single-use numeric tokens. The tokens
are generated using the RFC6238 algorithm with the X/Y coordinate as
the interval number. The "secret" seed values used here are base32-encoded
strings of length 16.

When deploying this, it's important to never use the same code twice. It's 
probably best to pick randomly from the set of codes you've never asked for.

See the example files, both generated with 'aaaaaaaaaaaaaaaa' as the secret.

- [Example PDF file](example.pdf)
- [Example text file](example.txt)

![Example as PNG](example.png "Example OTP Sheet")


## More about Coinkite

_Join The Most Powerful Bitcoin Platform_

Coinkite is the leading [bitcoin wallet](https://coinkite.com/faq/features) with
[multi-signature](https://coinkite.com/faq/multisig),
[bank-grade security](https://coinkite.com/faq/security),
[developer's API](https://coinkite.com/faq/developers) and [hardcore privacy](https://coinkite.com/privacy).

[Get Your Account Today!](https://coinkite.com/)
