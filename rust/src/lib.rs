#![allow(unused_imports)]

#[macro_use]
extern crate failure;

#[macro_use]
extern crate shippai_derive;

pub use shippai_derive::*;

#[macro_export]
macro_rules! shippai_export {
    () => {
        pub struct ShippaiError {
            error: ::failure::Error,
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

        #[no_mangle]
        pub unsafe extern "C" fn shippai_get_display(
            t: *mut ShippaiError,
        ) -> *const ::std::os::raw::c_char {
            use std::ffi::CString;
            CString::new(format!("{}", (*t).error)).unwrap().into_raw()
        }

        #[no_mangle]
        pub unsafe extern "C" fn shippai_get_debug(
            t: *mut ShippaiError,
        ) -> *const ::std::os::raw::c_char {
            use std::ffi::CString;
            CString::new(format!("{:?}", (*t).error))
                .unwrap()
                .into_raw()
        }

        #[no_mangle]
        pub unsafe extern "C" fn shippai_free_failure(t: *mut ShippaiError) {
            let _ = Box::from_raw(t);
        }

        #[no_mangle]
        pub unsafe extern "C" fn shippai_free_str(t: *mut ::std::os::raw::c_char) {
            use std::ffi::CString;
            CString::from_raw(t);
        }
    };
}

#[cfg(test)]
pub mod tests {
    use super::*;

    #[derive(Debug, Fail, Shippai)]
    enum MyError {
        #[fail(display = "Foo error")]
        Foo,
    }

    #[derive(Debug, Fail, Shippai)]
    enum MyOtherError {
        #[fail(display = "Bar error")]
        Bar,
    }

    shippai_export!();
}
