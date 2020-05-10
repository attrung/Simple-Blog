use `introflaskblogapp`;

CREATE TABLE `tbl_blog` (
`blog_id` int NOT NULL auto_increment,
`blog_title` VARCHAR(100) DEFAULT NULL,
`blog_content` VARCHAR(5000) DEFAULT null,
`blog_user_id` int DEFAULT null,
`blog_date` datetime DEFAULT NULL,
 PRIMARY KEY (`blog_id`) 
) ENGINE = InnoDB AUTO_INCREMENT =3 DEFAULT CHARSET= latin1;