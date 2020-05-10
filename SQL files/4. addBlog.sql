USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_addBlog`;

DELIMITER //

CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_addBlog`(
	IN p_title varchar(100),
	IN p_content varchar(5000),
	IN p_user_id int
)
BEGIN 
	insert into tbl_blog
		(
		blog_title,
		blog_content, 
        blog_user_id,
        blog_date
        )
        values
        (
			p_title,
            p_content,
			p_user_id,
            NOW()
		);
        
        SET @last_id = last_insert_id();
        insert into tbl_likes 
        (
			blog_id
        )
        values 
        (
			@last_id
        );
END //
DELIMITER ;
