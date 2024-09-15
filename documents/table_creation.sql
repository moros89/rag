CREATE TABLE documents (
    id INT NOT NULL AUTO_INCREMENT,
    content TEXT,
    vector blob,
    PRIMARY KEY (id)
)