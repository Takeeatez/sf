package com.example.sf.Repository;

import com.example.sf.Entity.FitnessEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface FitnessRepository extends JpaRepository<FitnessEntity, Integer> {
}
