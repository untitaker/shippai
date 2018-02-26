#[cfg(test)]
#[macro_use]
extern crate failure;
#[cfg(not(test))]
extern crate failure;

#[macro_export]
macro_rules! shippai_export {
    ($($err:path as $export_name:ident),*) => {
        pub struct ShippaiError {
            error: ::failure::Error
        }

        impl From<::failure::Error> for ShippaiError {
            fn from(e: ::failure::Error) -> ShippaiError {
                ShippaiError { error: e }
            }
        }

        impl From<ShippaiError> for ::failure::Error {
            fn from(e: ShippaiError) -> ::failure::Error {
                e.error
            }
        }

        #[allow(unreachable_code)]
        #[no_mangle]
        pub unsafe extern "C" fn shippai_get_cause_name(t: *mut ShippaiError)
            -> *const ::std::os::raw::c_char {
            use ::std::ffi::CString;
            use ::std::ptr;

            $(
                if (*t).error.downcast_ref::<$err>().is_some() {
                    return CString::new(stringify!($export_name)).unwrap().into_raw();
                }

                return ptr::null();
            )*
        }

        static SHIPPAI_CAUSE_NAMES: &'static str = concat!( $( stringify!($export_name), "," ),* );

        #[no_mangle]
        pub unsafe extern "C" fn shippai_get_cause_names() -> *const ::std::os::raw::c_char {
            use ::std::ffi::CString;
            // How to get rid of this entire function?
            CString::new(SHIPPAI_CAUSE_NAMES).unwrap().into_raw()
        }

        #[no_mangle]
        pub unsafe extern "C" fn shippai_get_cause_display(t: *mut ShippaiError)
            -> *const ::std::os::raw::c_char {
            use ::std::ffi::CString;
            CString::new(format!("{}", (*t).error)).unwrap().into_raw()
        }

        #[no_mangle]
        pub unsafe extern "C" fn shippai_get_debug(t: *mut ShippaiError)
            -> *const ::std::os::raw::c_char {
            use ::std::ffi::CString;
            CString::new(format!("{:?}", (*t).error)).unwrap().into_raw()
        }

        #[no_mangle]
        pub unsafe extern "C" fn shippai_free_failure(t: *mut ShippaiError) {
            let _ = Box::from_raw(t);
        }

        #[no_mangle]
        pub unsafe extern "C" fn shippai_free_str(t: *mut ::std::os::raw::c_char) {
            use ::std::ffi::CString;
            CString::from_raw(t);
        }
    }

}

#[cfg(test)]
pub mod tests {
    use super::*;

    #[derive(Debug, Fail)]
    enum MyError {
        #[fail(display = "Foo error")]
        Foo,
    }

    #[derive(Debug, Fail)]
    enum MyOtherError {
        #[fail(display = "Bar error")]
        Bar,
    }

    shippai_export!{
        MyError as MY_ERROR,
        MyOtherError as MY_OTHER_ERROR
    }

    pub unsafe extern "C" fn get_foo_error() -> *mut failure::Error {
        Box::into_raw(Box::new(MyError::Foo.into()))
    }

    pub unsafe extern "C" fn get_bar_error() -> *mut failure::Error {
        Box::into_raw(Box::new(MyOtherError::Bar.into()))
    }
}
