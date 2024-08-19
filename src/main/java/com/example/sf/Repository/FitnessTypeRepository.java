package com.example.sf.Repository;

import com.example.sf.Entity.FitnessTypeEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FitnessTypeRepository extends JpaRepository<FitnessTypeEntity, Integer> {
}
