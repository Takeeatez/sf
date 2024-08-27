package com.example.sf.Service;

import com.example.sf.Repository.UserRepository;
import jakarta.transaction.Transactional;
import lombok.Getter;
import lombok.RequiredArgsConstructor;
import lombok.Setter;
import org.springframework.stereotype.Service;

import java.security.Principal;

@Service
@Getter
@Setter
@RequiredArgsConstructor
@Transactional
public class IdCheckService {

    private final UserRepository userRepository;

    public Long IdCheck(Principal principal){
        String userId = principal.getName();
        return userRepository.findUserNoByUserId(userId);
    }
}