import editdistance as edt


def get_best_result(data, value):
    if type(data) == set:
        m = min(list(data), key=lambda x: edt.eval(x.lower(), value))
        if edt.eval(m.lower(), value) > 2:
            return None
        return m
    elif type(data) == dict:
        m = min(data.keys(), key=lambda x: edt.eval(data[x].lower(), value))
        if edt.eval(data[m].lower(), value) > 2:
            return None
        return m
    else:
        raise NotImplementedError
