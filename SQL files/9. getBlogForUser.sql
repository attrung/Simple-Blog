USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_GetBlogByUser`;

DELIMITER //
USE `IntroFlaskBlogApp` //
CREATE PROCEDURE `sp_GetBlogByUser` (
IN p_user_id bigint
)
BEGIN
	SELECT * from tbl_blog where blog_user_id = p_user_id;
END//

DELIMITER ;

