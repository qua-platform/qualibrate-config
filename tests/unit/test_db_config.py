import pytest

from qualibrate_config.models import DBConfig


def test_db_config_minimal():
    """Test DBConfig with only required fields."""
    config_dict = {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
    }
    db_config = DBConfig(config_dict)

    assert db_config.host == "localhost"
    assert db_config.port == 5432
    assert db_config.database == "test_db"
    assert db_config.username is None
    assert db_config.password is None
    assert db_config.is_connected is False


def test_db_config_full():
    """Test DBConfig with all fields."""
    config_dict = {
        "host": "db.example.com",
        "port": 3306,
        "database": "production_db",
        "username": "admin",
        "password": "secret123",
        "is_connected": True,
    }
    db_config = DBConfig(config_dict)

    assert db_config.host == "db.example.com"
    assert db_config.port == 3306
    assert db_config.database == "production_db"
    assert db_config.username == "admin"
    assert db_config.password == "secret123"
    assert db_config.is_connected is True


def test_db_config_missing_required_field():
    """Test that DBConfig raises error when required fields are missing."""
    config_dict = {
        "host": "localhost",
        "port": 5432,
        # missing 'database'
    }
    with pytest.raises(ValueError):
        DBConfig(config_dict)


def test_db_config_wrong_type():
    """Test that DBConfig validates field types."""
    config_dict = {
        "host": "localhost",
        "port": "not_a_number",  # should be int
        "database": "test_db",
    }
    with pytest.raises(ValueError):
        DBConfig(config_dict)


def test_db_config_serialization():
    """Test that DBConfig can be serialized back to dict."""
    config_dict = {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "user",
    }
    db_config = DBConfig(config_dict)
    serialized = db_config.serialize()

    assert serialized == {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "username": "user",
        "is_connected": False,
    }


def test_db_config_serialization_exclude_none():
    """Test that None values are excluded when serializing."""
    config_dict = {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
    }
    db_config = DBConfig(config_dict)
    serialized = db_config.serialize(exclude_none=True)

    # username and password should not be in serialized output
    assert "username" not in serialized
    assert "password" not in serialized
    assert serialized == {
        "host": "localhost",
        "port": 5432,
        "database": "test_db",
        "is_connected": False,
    }
