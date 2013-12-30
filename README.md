Ankov
=====

The Internet Beast

In short:

Ankov.py is the brain of the program, if you will.

It spawns up tentacles (or, threads) that connect to various online services, such as IRC or reddit. These 
tentacles are defined by classes defined in the tentacles/ directory, and must inherit from the Tentacle
class defined in tentacles/tentacle_base.py in order to use shared tentacle functionality (such as reporting
back to the main Ankov thread).

In each of these tentacles, a shared database of text is created based on scraped text from the services. 

This shared database of text is used to generate strings of english (currently done with ngram markov chains)
that enable the tentacles to respond to people on their various services and pretend to be just another user.
The benefit of a shared database is that the more services (and, moreso, threads per service) spun up, the more
that is scraped and the better the generated text will be.

In the memory/ directory (after running the script), you will find serialized version of the raw language graph
generated by scraping connected services. In the corpus/ directory, you will find free TXT books that let you
jumpstart your english database by calling speech_markov_instance.load('corpus/book_name.txt').
