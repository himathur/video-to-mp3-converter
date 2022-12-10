CREATE DATABASE auth;

CREATE USER 'auth_user'@'%' identified by 'auth123';

GRANT ALL PRIVILEGES ON auth.* to 'auth_user'@'%';

USE auth;

create TABLE user (
    id int not null AUTO_INCREMENT PRIMARY KEY,
    email varchar(255) not null UNIQUE,
    password varchar(255) not null
);

INSERT into user (email, password) values ('himanshu@gmail.com','himanshu')