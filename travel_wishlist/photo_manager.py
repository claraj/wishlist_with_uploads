import logging

# photo is an ImageFieldFile object which has a convenient delete() method
def delete_photo(photo):
    logging.info('to do : delete photo at url %s' % photo)
    photo.delete()
