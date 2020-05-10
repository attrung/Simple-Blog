USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_addLike`;

DELIMITER //
USE `IntroFlaskBlogApp` //
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_addLike`(
	In p_blog_id int,
    IN p_user_id int
)
BEGIN 
insert into tbl_likes (
	blog_id,
	user_liked
)
 values (
	p_blog_id,
    p_user_id
);

END //
DELIMITER ;