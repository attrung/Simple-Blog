USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_GetUserById`;

DELIMITER //
USE `IntroFlaskBlogApp` //
CREATE PROCEDURE `sp_GetUserById` (
IN p_user_email varchar(100)
)
BEGIN
	SELECT * from blog_user where email = p_user_email;
END//

DELIMITER ;