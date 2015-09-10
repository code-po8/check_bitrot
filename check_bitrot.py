#!/usr/bin/env python

#=============#
#   imports   #
#=============#
import hashlib #for file checksum-ing
import os #for filesystem walking
import sys #for command-line arguments

#===============#
#   constants   #
#===============#
CHECKSUM_FILE_SUFFIX = '.md5'
CHECKSUM_HASHING_METHOD = hashlib.md5
DEFAULT_BLOCKSIZE = 65536
FILE_OPEN_READONLY = 'r'
FILE_OPEN_READONLY_BINARY = 'rb'
FILE_OPEN_WRITE = 'w'
STARTING_DIRECTORY = "."
VI_BKUP_SUFFIX = '~'

#===============#
#   utilities   #
#===============#
def isIgnoredFile(filename):
	""" Determines if the specified file should be ignored """

	#it should be ignored if it's a checksum file
	checkFileExtensionIndex = 0 - len(CHECKSUM_FILE_SUFFIX)
	fileExtension = filename[checkFileExtensionIndex:]
	isChecksumFile = (fileExtension == CHECKSUM_FILE_SUFFIX)
	
	#it should be ignored if it's a VI backup file
	isVIBackupFile = (filename[-1] == VI_BKUP_SUFFIX)

	return (isChecksumFile or isVIBackupFile)


def determineFileChecksum(filename, hashingMethod, blocksize=DEFAULT_BLOCKSIZE):
	""" returns a hex digest checksum of a given file using a configurable hashing method.
	    Example call would be:
	        determineFileChecksum('/home/user/file.txt',hashlib.md5())
	"""

	fileHandle = open(filename, FILE_OPEN_READONLY_BINARY)
	fileBuffer = fileHandle.read(blocksize)
	while(len(fileBuffer) > 0):
		hashingMethod.update(fileBuffer)
		fileBuffer = fileHandle.read(blocksize)
	return hashingMethod.hexdigest()

def getChecksum(checksumFilename):
	""" returns a checksum from a file """

	#raise NotImplemented('error: getChecksum() method not complete')
	checksumFileHandle = open(checksumFilename,FILE_OPEN_READONLY)
	existingChecksum = checksumFileHandle.read().strip()
	checksumFileHandle.close()
	return existingChecksum

def saveChecksum(checksumFilename,checksum):
	""" saves a checksum file """

	#raise NotImplemented('error: saveChecksum() method not complete')
	checksumFileHandle = open(checksumFilename,FILE_OPEN_WRITE)
	checksumFileHandle.write(checksum)
	checksumFileHandle.close()

#==========#
#   main   #
#==========#
def main(argList):
	""" main method """
	#initialize local vars
	checkFileExtensionIndex = 0 - len(CHECKSUM_FILE_SUFFIX)
	startingDirectory = STARTING_DIRECTORY
	numFilesChecked = 0

	#check if a custom starting directory was supplied and override
	if(len(argList) > 0):
		#override with first argument
		startingDirectory = argList[0]
	
	#walk the directory
	print "Checking '%s'..." % (startingDirectory)
	for root, dirs, files in os.walk(startingDirectory):
		path = root.split(os.sep)
		print "Current checking '%s'..." % (root)
		for filename in files:
			#check for ignored files
			if(not isIgnoredFile(filename)):
				#get the full path filename
				fullFilename = os.path.join(root,filename)

				#determine what the current checksum of the file is
				newFileChecksum = determineFileChecksum(fullFilename,CHECKSUM_HASHING_METHOD())

				#get the filename of the checksum file (which may or may not already exist)
				checksumFilename = fullFilename + CHECKSUM_FILE_SUFFIX

				#check to see if the checksum has already been saved for the file
				if(os.path.isfile(checksumFilename)):
					""" checksum file already exists.  check it """
					existingFileChecksum = getChecksum(checksumFilename)
					if(newFileChecksum != existingFileChecksum):
						print "ERROR: Mismatched checksums for %s" % (fullFilename)
						response = raw_input("Would you like to update the checksum? y/n: ")
						if(response.strip() == 'y'):
							print "Updating..."
							saveChecksum(checksumFilename,newFileChecksum)
					else:
						pass
				else:
					""" checksum file doesn't exist, create one """
					saveChecksum(checksumFilename,newFileChecksum)
					print "Saved checksum %s for %s" % (newFileChecksum,fullFilename)
				numFilesChecked += 1
			else:
				#this is an ignored file, no need to check
				pass
	print "Done. Checked %d files." % (numFilesChecked)

if __name__ == "__main__":
	main(sys.argv[1:]) #pass in command-line args, except for the first (program name)

