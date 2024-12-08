import os
import itertools
import random

def create_pairs(data_dir, is_positive):
    pairs = []
    labels = []
    
    # Iterate through each user's folder in the data_dir (either 'genuine' or 'forged')
    user_folders = os.listdir(data_dir)
    for user_folder in user_folders:
        user_path = os.path.join(data_dir, user_folder)
        images = [os.path.join(user_path, img) for img in os.listdir(user_path)]
        
        if is_positive:
            # Positive pairs: Two genuine signatures from the same user
            for pair in itertools.combinations(images, 2):
                pairs.append(pair)
                labels.append(1)
        else:
            # Negative pairs: Genuine + Forged signatures
            # For forged images, the user folder name has '_forged' appended
            genuine_user_folder = user_folder.replace('_forged', '')  # Remove '_forged' if present
            genuine_images_dir = os.path.join(data_dir.replace('forged', 'genuine'), genuine_user_folder)  # Point to genuine subfolder
            
            # Get genuine images from the correct subfolder in 'genuine'
            genuine_images = [
                os.path.join(genuine_images_dir, img)
                for img in os.listdir(genuine_images_dir)
            ]
            
            # Now `images` contains forged signatures
            forged_images = images
            
            # Generate negative pairs by pairing genuine images with forged images
            for genuine_img in genuine_images:
                forged_img = random.choice(forged_images)
                pairs.append((genuine_img, forged_img))
                labels.append(0)
    
    return pairs, labels

def prepare_data(train_genuine_dir, train_forged_dir):
    # Generate training pairs
    positive_pairs, positive_labels = create_pairs(train_genuine_dir, is_positive=True)
    negative_pairs, negative_labels = create_pairs(train_forged_dir, is_positive=False)

    # Combine and shuffle
    train_pairs = positive_pairs + negative_pairs
    train_labels = positive_labels + negative_labels
    combined = list(zip(train_pairs, train_labels))
    random.shuffle(combined)
    train_pairs, train_labels = zip(*combined)
    
    return list(train_pairs), list(train_labels)
