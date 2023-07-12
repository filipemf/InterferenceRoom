package com.filipeferreira.interferenceroom.registration;

import com.filipeferreira.interferenceroom.appuser.AppUser;
import com.filipeferreira.interferenceroom.appuser.AppUserRole;
import com.filipeferreira.interferenceroom.appuser.AppUserService;
import com.filipeferreira.interferenceroom.email.EmailSender;
import com.filipeferreira.interferenceroom.registration.token.ConfirmationToken;
import com.filipeferreira.interferenceroom.registration.token.ConfirmationTokenService;
import lombok.AllArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@AllArgsConstructor
public class RegistrationService {

    private final AppUserService appUserService;
    private final EmailValidator emailValidator;
    private final ConfirmationTokenService confirmationTokenService;
    private final EmailSender emailSender;

    public String register(RegistrationRequest request) {
        boolean isValidEmail = emailValidator.
                test(request.getEmail());

        if (!isValidEmail) {
            throw new IllegalStateException("email not valid");
        }

        String token = appUserService.signUpUser(
                new AppUser(
                        request.getFirstName(),
                        request.getLastName(),
                        request.getEmail(),
                        request.getPassword(),
                        AppUserRole.USER

                )
        );

        String link = "http://localhost:8080/api/v1/registration/confirm?token=" + token;
        emailSender.send(
                request.getEmail(),
                buildEmail(request.getFirstName(), link));

        return token;
    }

    @Transactional
    public String confirmToken(String token) {
        ConfirmationToken confirmationToken = confirmationTokenService
                .getToken(token)
                .orElseThrow(() ->
                        new IllegalStateException("token not found"));

        if (confirmationToken.getConfirmedAt() != null) {
            throw new IllegalStateException("email already confirmed");
        }

        LocalDateTime expiredAt = confirmationToken.getExpiresAt();

        if (expiredAt.isBefore(LocalDateTime.now())) {
            throw new IllegalStateException("token expired");
        }

        confirmationTokenService.setConfirmedAt(token);
        appUserService.enableAppUser(
                confirmationToken.getAppUser().getEmail());
        return "confirmed";
    }

    private String buildEmail(String name, String link) {
        return "<div style=\"font-family: 'Roboto', Arial, sans-serif; font-size: 16px; margin: 0; color: #0b0c0c;\">\n" +
                "<table role=\"presentation\" width=\"100%\" style=\"border-collapse: collapse; min-width: 100%; width: 100%!important;\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\">\n" +
                "    <tr>\n" +
                "        <td width=\"100%\" height=\"53\" bgcolor=\"#0b0c0c\">\n" +
                "            <table role=\"presentation\" width=\"100%\" style=\"border-collapse: collapse; max-width: 580px;\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" align=\"center\">\n" +
                "                <tr>\n" +
                "                    <td width=\"70\" bgcolor=\"#0b0c0c\" valign=\"middle\">\n" +
                "                        <table role=\"presentation\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-collapse: collapse;\">\n" +
                "                            <tr>\n" +
                "                                <td style=\"padding-left: 10px;\"></td>\n" +
                "                                <td style=\"font-size: 28px; line-height: 1.315789474; margin-top: 4px; padding-left: 10px;\">\n" +
                "                                    <span style=\"font-family: 'Roboto', Arial, sans-serif; font-weight: 700; color: #ffffff; text-decoration: none; vertical-align: top; display: inline-block;\">Confirm Your Email</span>\n" +
                "                                </td>\n" +
                "                            </tr>\n" +
                "                        </table>\n" +
                "                    </td>\n" +
                "                </tr>\n" +
                "            </table>\n" +
                "        </td>\n" +
                "    </tr>\n" +
                "</table>\n" +
                "<table role=\"presentation\" class=\"content\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-collapse: collapse; max-width: 580px; width: 100%!important;\" width=\"100%\">\n" +
                "    <tr>\n" +
                "        <td width=\"10\" height=\"10\" valign=\"middle\"></td>\n" +
                "        <td>\n" +
                "            <table role=\"presentation\" width=\"100%\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-collapse: collapse;\">\n" +
                "                <tr>\n" +
                "                    <td bgcolor=\"#1D70B8\" width=\"100%\" height=\"10\"></td>\n" +
                "                </tr>\n" +
                "            </table>\n" +
                "        </td>\n" +
                "        <td width=\"10\" valign=\"middle\" height=\"10\"></td>\n" +
                "    </tr>\n" +
                "</table>\n" +
                "<table role=\"presentation\" class=\"content\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\" border=\"0\" style=\"border-collapse: collapse; max-width: 580px; width: 100%!important;\" width=\"100%\">\n" +
                "    <tr>\n" +
                "        <td height=\"30\"><br></td>\n" +
                "    </tr>\n" +
                "    <tr>\n" +
                "        <td width=\"10\" valign=\"middle\"><br></td>\n" +
                "        <td style=\"font-family: 'Roboto', Arial, sans-serif; font-size: 19px; line-height: 1.315789474; max-width: 560px;\">\n" +
                "            <p style=\"margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0b0c0c;\">Hi " + name + ",</p>\n" +
                "            <p style=\"margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0b0c0c;\">Thank you for registering. Please click on the link below to activate your account:</p>\n" +
                "            <blockquote style=\"margin: 0 0 20px 0; border-left: 10px solid #b1b4b6; padding: 15px 0 0.1px 15px; font-size: 19px; line-height: 25px;\">\n" +
                "                <p style=\"margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0b0c0c;\">\n" +
                "                    <a href=\"" + link + "\">Activate Now</a>\n" +
                "                </p>\n" +
                "            </blockquote>\n" +
                "            <p style=\"margin: 0 0 20px 0; font-size: 19px; line-height: 25px; color: #0b0c0c;\">The link will expire in 15 minutes.</p>\n" +
                "            <p>See you soon!</p>\n" +
                "        </td>\n" +
                "        <td width=\"10\" valign=\"middle\"><br></td>\n" +
                "    </tr>\n" +
                "    <tr>\n" +
                "        <td height=\"30\"><br></td>\n" +
                "    </tr>\n" +
                "</table>\n" +
                "</div>";
    }
}
