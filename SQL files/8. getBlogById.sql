USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_GetBlogById`;

DELIMITER //
USE `IntroFlaskBlogApp` //
CREATE PROCEDURE `sp_GetBlogById` (
IN p_blog_id bigint
)
BEGIN
	SELECT * from tbl_blog where blog_id = p_blog_id;
END//

DELIMITER ;