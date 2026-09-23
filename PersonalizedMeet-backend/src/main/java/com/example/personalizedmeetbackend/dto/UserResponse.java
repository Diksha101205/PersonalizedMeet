package com.example.personalizedmeetbackend.dto;

import java.time.LocalDateTime;

import com.example.personalizedmeetbackend.model.Role;

public class UserResponse {

    private Long id;
    private String name;
    private String email;
    private Role role;
    private LocalDateTime createdAt;

    public UserResponse(Long id, String name, String email, Role role, LocalDateTime createdAt) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.role = role;
        this.createdAt = createdAt;
    }

    public Long getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public String getEmail() {
        return email;
    }

    public Role getRole() {
        return role;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
}
