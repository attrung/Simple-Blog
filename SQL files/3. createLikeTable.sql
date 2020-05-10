use `introflaskblogapp`;


CREATE TABLE `tbl_likes` (
`like_id` int NOT NULL auto_increment,
`blog_id` int DEFAULT NULL,
`user_liked` int DEFAULT NULL,
primary key (`like_id`) 
) ENGINE = InnoDB AUTO_INCREMENT =3 DEFAULT CHARSET= latin1;
