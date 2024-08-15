package com.example.sf.DTO;

import lombok.*;

@Data
@Builder
@ToString
@AllArgsConstructor
@NoArgsConstructor
public class UserDTO {
    private Long id;
    private String userId;
    private String userName;
    private String password;
    private String email;
    private String phone;

    // 필요에 따라 비밀번호를 포함할 수도 있지만 보통 보안을 위해 제외
}
