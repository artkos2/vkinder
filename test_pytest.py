import pytest
from vk_ import *
from bd_ import *


@pytest.mark.parametrize('owner, result', [(250740570, [399755775, 360089094, 342931342]), (356913, [280263122,278216503,278216471])])
def test_get_photos(owner, result):
    assert get_photos(owner) == result