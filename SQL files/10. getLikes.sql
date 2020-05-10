USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_GetLikeByBlogId`;

DELIMITER //
USE `IntroFlaskBlogApp` //
CREATE PROCEDURE `sp_GetLikeByBlogId` (
IN p_blog_id bigint
)
BEGIN
	SELECT user_id, name, blog_id FROM tbl_likes p 
    INNER JOIN blog_user c
    on c.user_id = p.user_liked
    where blog_id = p_blog_id;
END//

DELIMITER ;