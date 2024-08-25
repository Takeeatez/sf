package com.example.sf.Service;

import com.example.sf.DTO.UserDTO;
import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.modelmapper.ModelMapper;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.security.Principal;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class UserService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final ModelMapper modelMapper;

    // 현재 로그인된 사용자의 userName 가져오기
    public String getLoggedInUserName() {
        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();

        if (authentication == null || !authentication.isAuthenticated()) {
            throw new RuntimeException("User is not authenticated");
        }

        Object principal = authentication.getPrincipal();
        if (principal instanceof UserDetails) {
            return ((UserDetails) principal).getUsername();
        } else {
            return principal.toString();
        }
    }

    public UserDTO getLoggedInUserDetails() {
        String username = getLoggedInUserName(); // 현재 로그인한 사용자의 username을 가져옴
        System.out.println("Logged in username: " + username); // 로그 추가

        UserEntity userEntity = userRepository.findByUserName(username)
                .orElseThrow(() -> new RuntimeException("User not found with username: " + username));

        return convertToDTO(userEntity);
    }

    // 사용자 생성 (회원가입)
    public UserDTO createUser(UserDTO userDTO) {
        // 비밀번호 암호화
        String encodedPassword = passwordEncoder.encode(userDTO.getPassword());

        // User 엔티티 생성
        UserEntity userEntity = UserEntity.builder()
                .userId(userDTO.getUserId())
                .password(encodedPassword)
                .userName(userDTO.getUserName())
                .email(userDTO.getEmail())
                .phone(userDTO.getPhone())
                .role(UserEntity.Role.USER) // 기본 역할은 USER
                .build();

        // 사용자 저장
        UserEntity savedUserEntity = userRepository.save(userEntity);

        // 저장된 사용자 정보를 DTO로 변환하여 반환
        return convertToDTO(savedUserEntity);
    }

    // 사용자 조회 (ID로)
    public UserDTO getUserById(Long id) {
        UserEntity userEntity = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return convertToDTO(userEntity);
    }

    // 사용자 조회 (사용자 아이디로)
    public UserDTO getUserByUserId(String userId) {
        UserEntity userEntity = userRepository.findByUserId(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return convertToDTO(userEntity);
    }

    // 로그인된 사용자 userName받아옴
    public String getUserName(Principal principal){
        return principal.getName();
    }

    public UserDTO getUserInfo(String userName) {
        UserEntity userEntity = userRepository.findUserEntityByUserId(userName);

        // ModelMapper를 사용해 UserEntity를 UserDTO로 변환
        return modelMapper.map(userEntity, UserDTO.class);
    }

    // 사용자 이름으로 조회
    public String getUserByUserName(String userName) {
        return userRepository.findUserNameByUserId(userName);
    }

    // 사용자 목록 조회
    public List<UserDTO> getAllUsers() {
        return userRepository.findAll().stream()
                .map(this::convertToDTO)
                .collect(Collectors.toList());
    }

    // 사용자 정보 수정
    public UserDTO updateUser(Long id, UserDTO userDTO) {
        UserEntity userEntity = userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("User not found"));

        // 엔티티 필드 업데이트
        userEntity.setUserId(userDTO.getUserId());
        if (userDTO.getPassword() != null && !userDTO.getPassword().isEmpty()) {
            userEntity.setPassword(passwordEncoder.encode(userDTO.getPassword()));
        }
        userEntity.setUserName(userDTO.getUserName());
        userEntity.setEmail(userDTO.getEmail());
        userEntity.setPhone(userDTO.getPhone());

        // 사용자 저장
        UserEntity updatedUserEntity = userRepository.save(userEntity);
        return convertToDTO(updatedUserEntity);
    }

    // 사용자 삭제
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }

    // DTO를 엔티티로 변환
    private UserDTO convertToDTO(UserEntity userEntity) {
        return UserDTO.builder()
                .id(userEntity.getId())
                .userId(userEntity.getUserId())
                .userName(userEntity.getUserName())
                .email(userEntity.getEmail())
                .phone(userEntity.getPhone())
                .role(userEntity.getRole().name())
                .joinDate(userEntity.getJoinDate())
                .build();
    }
}
