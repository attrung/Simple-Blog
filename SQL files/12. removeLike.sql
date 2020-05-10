USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_removeLike`;

DELIMITER //
USE `IntroFlaskBlogApp` //
CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_removeLike`(
	In p_blog_id int,
    IN p_user_id int
)
BEGIN 
DELETE FROM tbl_likes WHERE p_blog_id = blog_id and p_user_id = user_liked;

END //
DELIMITER ;