# https://stackoverflow.com/a/71854211
def dundered(my_cls):
    def lift_method(cls_method_name):
        def lifted_method(cls, *args, **kwargs):
            return getattr(cls, cls_method_name)(*args, **kwargs)

        lifted_method.__name__ = f"__{cls_method_name[6:]}"
        return lifted_method

    meta_dict = dict()
    for key, val in dict(my_cls.__dict__).items():
        if key == f"__cls_{key[6:-2]}__":
            if not isinstance(val, classmethod):
                setattr(my_cls, key, classmethod(val))
            meta_dict[f"__{key[6:]}"] = lift_method(key)
    return type(f"{type(my_cls).__name__}_dunderable", (type(my_cls),), meta_dict)(
        my_cls.__name__ + "__", (my_cls,), {"__wrapped__": my_cls}
    )