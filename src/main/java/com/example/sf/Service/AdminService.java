package com.example.sf.Service;

import com.example.sf.Entity.FitnessEntity;
import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.FitnessRepository;
import com.example.sf.Repository.UserRepository;
import org.springframework.stereotype.Service;

@Service
public class AdminService {

    private final UserRepository userRepository;
    private final FitnessRepository fitnessRepository;

    public AdminService(UserRepository userRepository, FitnessRepository fitnessRepository) {
        this.userRepository = userRepository;
        this.fitnessRepository = fitnessRepository;
    }

    public void createUser(UserEntity user) {
        userRepository.save(user);
    }

    public void deleteUser(Long userId) {
        userRepository.deleteById(userId);
    }

    public void updateFitness(FitnessEntity fitness) {
        fitnessRepository.save(fitness);
    }


    // 기타 관리자 전용 기능들 추가
}
