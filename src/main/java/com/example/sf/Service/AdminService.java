package com.example.sf.Service;

import com.example.sf.Entity.FitnessTypeEntity;
import com.example.sf.Entity.UserEntity;
import com.example.sf.Repository.FitnessTypeRepository;
import com.example.sf.Repository.UserRepository;
import org.springframework.stereotype.Service;

@Service
public class AdminService {

    private final UserRepository userRepository;
    private final FitnessTypeRepository fitnessTypeRepository;

    public AdminService(UserRepository userRepository, FitnessTypeRepository fitnessTypeRepository) {
        this.userRepository = userRepository;
        this.fitnessTypeRepository = fitnessTypeRepository;
    }

    public void createUser(UserEntity user) {
        userRepository.save(user);
    }

    public void deleteUser(Long userId) {
        userRepository.deleteById(userId);
    }

    public void updateFitness(FitnessTypeEntity fitness) {
        fitnessTypeRepository.save(fitness);
    }

}
