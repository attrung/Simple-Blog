USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_GetAllBlogs`;
 
DELIMITER //
USE `IntroFlaskBlogApp`//
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_GetAllBlogs`()
BEGIN
	SELECT blog_id, blog_title, blog_content, blog_date, user_id, name FROM tbl_blog p
    INNER JOIN blog_user c
    ON c.user_id = p.blog_user_id
    ORDER BY
    blog_date;

END//
 
DELIMITER ;