"""
Product Management Page
Add, edit, and delete products
"""
import streamlit as st
import pandas as pd

def show():
    st.title("📦 Product Management")
    
    db = st.session_state.db_manager
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["View Products", "Add Product", "Edit Product"])
    
    # Tab 1: View Products
    with tab1:
        st.subheader("All Products")
        
        products = db.get_all_products()
        
        if products:
            df = pd.DataFrame([
                {
                    'ID': p['product_id'],
                    'Name': p['name'],
                    'Category': p['category'],
                    'Price': f"₹{p['price']:.2f}",
                    'Stock': p['stock'],
                    'Class Name': p['class_name']
                }
                for p in products
            ])
            
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Products", len(products))
            with col2:
                st.metric("Total Stock", sum(p['stock'] for p in products))
            with col3:
                st.metric("Categories", len(set(p['category'] for p in products)))
        else:
            st.info("No products found. Add a product to get started!")
    
    # Tab 2: Add Product
    with tab2:
        st.subheader("Add New Product")
        
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("Product Name")
            category = st.text_input("Category")
            price = st.number_input("Price (₹)", min_value=0.0, step=0.1)
        
        with col2:
            stock = st.number_input("Initial Stock", min_value=0, step=1)
            class_name = st.text_input("YOLO Class Name", 
                                      help="The class name that YOLO model recognizes")
            image_path = st.text_input("Image Path (optional)")
        
        if st.button("➕ Add Product", use_container_width=True):
            if product_name and category and class_name:
                product_id = db.add_product(
                    name=product_name,
                    category=category,
                    price=price,
                    stock=stock,
                    class_name=class_name,
                    image_path=image_path
                )
                
                if product_id:
                    st.success(f"✅ Product added successfully! (ID: {product_id})")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Product with this name already exists!")
            else:
                st.warning("⚠️ Please fill all required fields")
    
    # Tab 3: Edit Product
    with tab3:
        st.subheader("Edit Product")
        
        products = db.get_all_products()
        
        if products:
            # Select product
            product_options = {p['name']: p['product_id'] for p in products}
            selected_product_name = st.selectbox("Select Product", 
                                                  product_options.keys())
            
            if selected_product_name:
                product_id = product_options[selected_product_name]
                product = db.get_product_by_id(product_id)
                
                st.write("---")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_price = st.number_input(
                        "Price (₹)",
                        value=product['price'],
                        step=0.1
                    )
                    new_stock = st.number_input(
                        "Stock",
                        value=product['stock'],
                        step=1
                    )
                
                with col2:
                    new_category = st.text_input(
                        "Category",
                        value=product['category']
                    )
                    new_class_name = st.text_input(
                        "YOLO Class Name",
                        value=product['class_name']
                    )
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✏️ Update Product", use_container_width=True):
                        if db.update_product(
                            product_id,
                            price=new_price,
                            stock=new_stock,
                            category=new_category,
                            class_name=new_class_name
                        ):
                            st.success("✅ Product updated successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Error updating product")
                
                with col2:
                    if st.button("🗑️ Delete Product", use_container_width=True):
                        if db.delete_product(product_id):
                            st.success("✅ Product deleted successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Error deleting product")
        else:
            st.info("No products found")
