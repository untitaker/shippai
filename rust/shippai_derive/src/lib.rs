extern crate proc_macro;
extern crate proc_macro2;
extern crate syn;
#[macro_use]
extern crate quote;

use proc_macro::TokenStream;

#[proc_macro_derive(Shippai)]
pub fn shippai(input: TokenStream) -> TokenStream {
    let ast = syn::parse(input).unwrap();
    let gen = impl_shippai(&ast);
    gen.into()
}

fn impl_shippai(ast: &syn::DeriveInput) -> quote::Tokens {
    let error_name = &ast.ident;
    let fn_name = proc_macro2::Term::new(
        &format!("shippai_is_error_{}", error_name),
        proc_macro2::Span::call_site()
    );
    quote! {
        #[no_mangle]
        pub unsafe extern "C" fn #fn_name(t: *mut ShippaiError) -> bool {
            (*t).error.downcast_ref::<#error_name>().is_some()
        }
    }
}
