DELIMITER //

CREATE DEFINER = `root`@`localhost` PROCEDURE `sp_validateLogin` (
IN p_email VARCHAR (100)
)
BEGIN
	select * from blog_user where email = p_email;
END //

