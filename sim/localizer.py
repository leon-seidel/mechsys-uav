def pixel_to_ground(u, v, altitude, K):
    # Compute the offset of the pixel from the principal point
    u_prime = u - K[0, 2]
    v_prime = v - K[1, 2]

    # Convert pixel offsets to normalized image coordinates
    image_x_norm = u_prime / K[0, 0]
    image_y_norm = v_prime / K[1, 1]

    # Backproject onto the ground plane using similar triangles
    ground_y = altitude * image_x_norm
    ground_x = - altitude * image_y_norm

    return ground_x, ground_y
