import pytest

from panther_seim import Panther

def test_panther_init_input_types_1():
    """Token is not a string."""
    with pytest.raises(ValueError):
        Panther(123, "acme.runpanther.net")

def test_panther_init_input_types_2():
    """Domain is not a string."""
    with pytest.raises(ValueError):
        Panther("token", 123)

@pytest.mark.parametrize("domain", [
    "https://acme.runpanther.net",
    "https://acme.runpanther.net/",
    "acme.runpanther.net/",
    "1x.this-domain-starts-with-a-digit.com",
    ".this-domain-starts-with-a-dot.com"
    "this-domain-ends-with-a-dot."
]
)
def test_panther_init_invalid_domain(domain):
    """Domain value is not in proper format."""
    with pytest.raises(ValueError):
        Panther("token", domain)

@pytest.mark.parametrize("domain", [
    "acme.runpanther.net",
    "panther.security.acme.com",
    "panther-instance.acme.com",
    "fairytale-name.runpanther.net"
]
)
def test_panther_init_valid_domain(domain):
    """Domain value is valid and shouldn't raise any exceptions."""
    Panther("token", domain)

