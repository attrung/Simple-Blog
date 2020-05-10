USE `IntroFlaskBlogApp`;
DROP procedure IF EXISTS `sp_createUser`;

DELIMITER //
USE `IntroFlaskBlogApp` //

CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_createUser`(
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(100),
    IN p_name VARCHAR(100),
    IN p_phone_num VARCHAR(100),
    IN p_job VARCHAR(100),
    In p_platform VARCHAR(10)
)
BEGIN
    IF ( select exists (select 1 from blog_user where email = p_email) ) THEN
     
        select 'Email Exists !!';
     
    ELSE
     
        insert into blog_user
        (
            email,
            password,
            name,
            phone_num,
            job,
            platform
        )
        values
        (
            p_email,
            p_password,
            p_name,
            p_phone_num,
            p_job,
            p_platform
        );
     
    END IF;
END //

DELIMITER ;