iinit
ils

iadmin mkuser alice#tempZone rodsuser
imeta add -u alice a v u

iadmin mksuer smithers#tempZone rodsadmin
imeta add -u smithers a v u

iadmin mkuser bob#tempZone rodsuser
imeta add -u bob a v u

for ((i=1 ; i<=5 ; i++)) ; do
	rm "file_$i.txt"
	fallocate -l 1M "file_$i.txt"

	iadmin mkresc "resc_$i" unixfilesystem `hostname`:/var/lib/irods/vault_$i
	imeta add -R "resc_$i" a v u
done


for ((i=1 ; i<=5 ; i++)) ; do
	imkdir "collection_$i"
	imeta add -C "collection_$i" a v u
	icd "collection_$i"
	for ((j=1 ; j<=5 ; j++)) ; do
		iput "file_$j.txt"
		imeta add -d "file_$j.txt" a v u 
		iticket create read "file_$j.txt"
	done
	icd ..
done


