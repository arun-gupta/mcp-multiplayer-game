FROM python:3.11.13

COPY bc-1.08.2.tar.gz /bc-1.08.2.tar.gz
RUN tar -xvzf bc-1.08.2.tar.gz

WORKDIR /bc-1.08.2
RUN ln -s $(which true) /usr/bin/makeinfo
RUN ./configure  
RUN make 
RUN make install

WORKDIR /
RUN rm -r bc-1.08.2
RUN rm bc-1.08.2.tar.gz

WORKDIR /gupta

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
