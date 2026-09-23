package com.example.personalizedmeetbackend.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.example.personalizedmeetbackend.dto.UserRequest;
import com.example.personalizedmeetbackend.dto.UserResponse;
import com.example.personalizedmeetbackend.exception.DuplicateEmailException;
import com.example.personalizedmeetbackend.exception.UserNotFoundException;
import com.example.personalizedmeetbackend.model.User;
import com.example.personalizedmeetbackend.repository.UserRepository;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    public UserResponse createUser(UserRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new DuplicateEmailException(request.getEmail());
        }

        User user = new User();
        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setPassword(request.getPassword());
        user.setRole(request.getRole());

        User savedUser = userRepository.save(user);
        return mapToResponse(savedUser);
    }

    public UserResponse getUserById(Long id) {
        User user = findUserOrThrow(id);
        return mapToResponse(user);
    }

    public List<UserResponse> getAllUsers() {
        return userRepository.findAll()
                .stream()
                .map(this::mapToResponse)
                .toList();
    }

    public UserResponse updateUser(Long id, UserRequest request) {
        User user = findUserOrThrow(id);

        userRepository.findByEmail(request.getEmail())
                .filter(existingUser -> !existingUser.getId().equals(id))
                .ifPresent(existingUser -> {
                    throw new DuplicateEmailException(request.getEmail());
                });

        user.setName(request.getName());
        user.setEmail(request.getEmail());
        user.setPassword(request.getPassword());
        user.setRole(request.getRole());

        User updatedUser = userRepository.save(user);
        return mapToResponse(updatedUser);
    }

    public void deleteUser(Long id) {
        User user = findUserOrThrow(id);
        userRepository.delete(user);
    }

    private User findUserOrThrow(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new UserNotFoundException(id));
    }

    private UserResponse mapToResponse(User user) {
        return new UserResponse(
                user.getId(),
                user.getName(),
                user.getEmail(),
                user.getRole(),
                user.getCreatedAt()
        );
    }
}
