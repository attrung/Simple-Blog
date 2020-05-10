CREATE DATABASE introflaskblogapp;

CREATE TABLE `introFlaskBlogApp`.`blog_user` (
  `user_id` BIGINT NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(100) NULL,
  `name` varchar(100) null,
  `phone_num` varchar(100) null,
  `job` varchar(100) null,
  `platform` varchar(100) null,
  `password` varchar(100) null,
  PRIMARY KEY (`user_id`));

