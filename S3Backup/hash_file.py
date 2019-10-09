import hashlib
import os
from shutil import move
from tempfile import mkstemp

BLOCKSIZE = 65535


def find_hash(hash_file, plan_name):
    # Try to find the hash in the hash file
    filename = os.path.normpath(hash_file)
    if os.path.isfile(filename):
        plan_hashes = open(filename, 'r').readlines()
        for line in plan_hashes:
            parts = line.strip().split('=')
            if len(parts) == 2 and parts[0] == plan_name:
                return parts[1]

    return None


def update_hash(hash_file, plan_name, hash_value):
    # Do the update (create the file if it doesn't exist)
    filename = os.path.normpath(hash_file)

    # If it doesn't exist, we shortcut this
    if not os.path.isfile(hash_file):
        with open(hash_file, 'w') as new_file:
            new_file.write('%s=%s\n' % (plan_name, hash_value))
        return

    # Otherwise, we need to rebuild the file
    fh, abs_path = mkstemp()
    is_written = False

    with open(abs_path, 'w') as new_file:
        with open(filename, 'r') as old_file:
            # Handle existing entries in the file
            for line in old_file:
                parts = line.strip().split('=')
                if parts[0] == plan_name:
                    is_written = True
                    new_file.write('%s=%s\n' % (plan_name, hash_value))
                else:
                    new_file.write(line)

            # If the hash wasn't already in the file
            if not is_written:
                new_file.write('%s=%s\n' % (plan_name, hash_value))

    os.close(fh)

    # Remove original file
    os.remove(hash_file)

    # Move new file
    move(abs_path, hash_file)


def calc_hash(filename):
    hasher = hashlib.md5()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()
