from python_backend.security import derive_document_key


def test_derive_document_key_changes_with_content():
    k1 = derive_document_key("/path/to/doc.pdf", b"abc")
    k2 = derive_document_key("/path/to/doc.pdf", b"abcd")
    assert k1 != k2 and len(k1) == 32 and len(k2) == 32


