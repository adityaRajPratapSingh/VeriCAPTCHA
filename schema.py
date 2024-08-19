def serialise_1(obj)->dict:
    return{
        "id":str(obj['_id']),
        "username":obj['username'],
        "email": obj['email'],
        "full_name":obj['full_name'],
        "disabled":obj['disabled'],
        "score":obj['score'],
        "hashed_password":obj['hashed_password']
    }

def serialise_2(obj)->dict:
    return{
        "id":str(obj['_id']),
        "sentence":obj['sentence'],
        "label": obj['label']
    }

def serealise_3(obj)->dict:
    return{
        "id":str(obj['_id']),
        "label_class":obj['label_class'],
        'label':obj['label']
    }